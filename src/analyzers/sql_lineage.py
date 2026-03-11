import re
import json
import hashlib
import sqlglot
from sqlglot import exp, parse_one
from sqlglot.optimizer.qualify import qualify
from sqlglot.optimizer.scope import build_scope
from typing import List, Optional, Dict, Tuple, Any
from models.lineage import LineageEdge, ColumnRef

class SQLLineageAnalyzer:
    """Uses sqlglot to extract lineage from SQL and dbt models with Phase 2.5 refinements."""
    
    def __init__(self, default_dialect: str = "duckdb"):
        self.default_dialect = default_dialect

    def _generate_logic_hash(self, sql: str) -> str:
        """Generates a stable, whitespace-insensitive hash for SQL content."""
        if not sql: return "unknown"
        normalized = re.sub(r"__dbt_ref_([a-zA-Z0-9_]+)__", r"\1", sql)
        normalized = re.sub(r"__dbt_source_([a-zA-Z0-9_]+)_([a-zA-Z0-9_]+)__", r"\1.\2", normalized)
        normalized = " ".join(normalized.lower().split()).strip()
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]

    def _mock_jinja(self, sql: str) -> str:
        """Mocks dbt Jinja tags into parseable SQL identifiers."""
        sql = re.sub(r"\{\{\s*ref\s*\(\s*['\"]([^'\"]+)['\"]\s*\)\s*\}\}", r"__dbt_ref_\1__", sql)
        sql = re.sub(r"\{\{\s*source\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)\s*\}\}", r"__dbt_source_\1_\2__", sql)
        sql = re.sub(r"\{\{.*?\}\}", " ", sql)
        sql = re.sub(r"\{%.*?%\}", " ", sql, flags=re.DOTALL)
        return sql

    def _extract_tables(self, expression) -> List[str]:
        """Extracts external table names, completely filtering out CTE aliases via scope."""
        external_tables = set()
        root = build_scope(expression)
        if root:
            for scope in root.traverse():
                for alias, source in scope.sources.items():
                    if isinstance(source, exp.Table):
                        table_name = source.name.strip('"').strip("'").strip("`")
                        external_tables.add(table_name)
        return list(external_tables)

    def _extract_columns(self, expression, root_scope, schema=None, identity: str = "unknown") -> List[ColumnRef]:
        """Extracts projected column names and surgicaly resolves their sources."""
        def resolve_column_source(table_alias: str, column_name: str, scope, depth=0, visited=None) -> List[str]:
            if depth > 10: return []
            visited = visited or set()
            
            if not scope: 
                prefix = f"{table_alias}." if table_alias else ""
                return [f"{prefix}{column_name}"]
            
            # Step 1: Resolve Alias in Current Scope (Prioritize CTEs)
            source = scope.sources.get(table_alias)
            
            if isinstance(source, exp.Table):
                tname = source.name.strip('"').strip("'").strip("`")
                if tname.startswith("__dbt_ref_"): tname = tname[len("__dbt_ref_"):-2] if tname.endswith("__") else tname[len("__dbt_ref_"):]
                elif tname.startswith("__dbt_source_"):
                    tname = tname[len("__dbt_source_"):]
                    if tname.endswith("__"): tname = tname[:-2]
                    if "_" in tname: tname = tname.split("_")[-1]
                return [f"{tname}.{column_name}"]
            
            elif source.__class__.__name__ == "Scope":
                if id(source) in visited: return [f"{table_alias or 'unknown'}.{column_name}"]
                visited.add(id(source))
                
                for expr in source.expression.expressions:
                    if expr.alias_or_name == column_name:
                        val_cols = find_value_columns(expr)
                        if not val_cols: return [f"{table_alias or 'unknown'}.{column_name}"]
                        sources = []
                        for col in val_cols:
                            sources.extend(resolve_column_source(col.table, col.name, source, depth + 1, visited.copy()))
                        return list(dict.fromkeys(sources))
                
                # Star passthrough
                bases = []
                for alias in source.sources:
                    bases.extend(resolve_column_source(alias, column_name, source, depth + 1, visited.copy()))
                if bases: return list(dict.fromkeys(bases))

            # Step 2: Direct Schema Match
            if schema and table_alias and table_alias in schema:
                if column_name.lower() in schema[table_alias]:
                    tname = table_alias
                    if tname.startswith("__dbt_ref_"): tname = tname[len("__dbt_ref_"):-2] if tname.endswith("__") else tname[len("__dbt_ref_"):]
                    return [f"{tname}.{column_name}"]
            
            # Step 3: Handle Naked Columns
            if table_alias is None:
                bases = []
                for alias in scope.sources:
                    res = resolve_column_source(alias, column_name, scope, depth + 1, visited.copy())
                    if res:
                        source_obj = scope.sources.get(alias)
                        if isinstance(source_obj, exp.Table):
                            bases.extend([b if "." in b else f"{alias}.{b}" for b in res])
                        else: bases.extend(res)
                if bases: return list(dict.fromkeys(bases))
            
            # Step 4: Bubble up to Parent
            if scope.parent:
                if scope == root_scope: return [f"{table_alias or 'unknown'}.{column_name}"]
                return resolve_column_source(table_alias, column_name, scope.parent, depth + 1, visited)
            
            # Step 5: Global CTE Lookup
            if table_alias:
                clean_alias = table_alias.strip('"').strip("'").strip("`").lower()
                for sc in root_scope.traverse():
                    for alias, target in sc.sources.items():
                        if alias.strip('"').strip("'").strip("`").lower() == clean_alias:
                            if target.__class__.__name__ == "Scope" and id(target) not in visited:
                                return resolve_column_source(table_alias, column_name, target, depth + 1, visited.copy())

            prefix = f"{table_alias}." if table_alias else ""
            return [f"{prefix}{column_name}"]

        def find_value_columns(expr):
            if isinstance(expr, exp.Case):
                vals = []
                for case in expr.args.get("ifs", []):
                    vals.extend(find_value_columns(case.args.get("true")))
                if expr.args.get("default"): vals.extend(find_value_columns(expr.args.get("default")))
                return vals
            elif isinstance(expr, exp.AggFunc): return find_value_columns(expr.this)
            elif isinstance(expr, exp.Column): return [expr]
            elif isinstance(expr, exp.Alias): return find_value_columns(expr.this)
            elif isinstance(expr, (exp.Literal, exp.Null)): return []
            else:
                cols = []
                for arg_key, arg in expr.args.items():
                    if arg_key in ["on", "where", "having"]: continue
                    if isinstance(arg, list):
                        for sub in arg: 
                            if isinstance(sub, exp.Expression): cols.extend(find_value_columns(sub))
                    elif isinstance(arg, exp.Expression): cols.extend(find_value_columns(arg))
                return cols

        columns = []
        main_select = root_scope.expression
        if isinstance(main_select, exp.Select):
            # Pre-calculate internal aliases (CTEs only, not physical tables)
            internal_ctes = {alias.strip('"').strip("'").strip("`").lower() for sc in root_scope.traverse() for alias, target in sc.sources.items() if not isinstance(target, exp.Table)}
            dbt_keywords = {"source", "ref", "renamed", "stg", "final", "base"} | internal_ctes

            for item in main_select.expressions:
                name = item.alias if isinstance(item, exp.Alias) else item.alias_or_name
                source_cols = []
                if isinstance(item, exp.Star):
                    for alias in root_scope.sources: source_cols.extend(resolve_column_source(alias, "*", root_scope))
                else:
                    v_cols = list(item.find_all(exp.Column))
                    if not v_cols: v_cols = find_value_columns(item)
                    for c in v_cols: source_cols.extend(resolve_column_source(c.table, c.name, root_scope))
                
                final_sources = set()
                for s in source_cols:
                    if "." in s:
                        prefix, col_res = s.split(".", 1)
                        clean_prefix = prefix.strip('"').strip("'").strip("`").lower()
                        if clean_prefix not in dbt_keywords: final_sources.add(s)
                        else:
                            peeled = False
                            for sc in root_scope.traverse():
                                for alias, target in sc.sources.items():
                                    if alias.strip('"').strip("'").strip("`").lower() == clean_prefix:
                                        if isinstance(target, exp.Table):
                                            tname = target.name.strip('"').strip("'").strip("`")
                                            if tname.startswith("__dbt_ref_"): tname = tname[len("__dbt_ref_"):-2] if tname.endswith("__") else tname[len("__dbt_ref_"):]
                                            elif tname.startswith("__dbt_source_"):
                                                tname = tname[len("__dbt_source_"):]
                                                if tname.endswith("__"): tname = tname[:-2]
                                                if "_" in tname: tname = tname.split("_")[-1]
                                            final_sources.add(f"{tname}.{col_res}"); peeled = True; break
                                        elif target.__class__.__name__ == "Scope":
                                            res = resolve_column_source(clean_prefix, col_res, target)
                                            for r in res:
                                                if "." in r:
                                                    r_prefix = r.split(".", 1)[0].strip('"').strip("'").strip("`").lower()
                                                    if r_prefix not in dbt_keywords: final_sources.add(r); peeled = True
                                                else: final_sources.add(r) # fallback
                                if peeled: break
                            if not peeled: final_sources.add(s)
                    else: final_sources.add(s)
                columns.append(ColumnRef(name=name, source_columns=sorted(list(final_sources)), confidence=1.0))
            
            seen_targets = {}
            for c in columns:
                if c.name not in seen_targets: seen_targets[c.name] = c
                else: seen_targets[c.name].source_columns = sorted(list(dict.fromkeys(seen_targets[c.name].source_columns + c.source_columns)))
            columns = sorted(seen_targets.values(), key=lambda x: x.name)
        return columns

    def analyze(self, filepath: str, identity: str, dialect: Optional[str] = None, schema: Optional[Dict] = None) -> Tuple[List[LineageEdge], Dict[str, List[ColumnRef]], Dict[str, Any]]:
        """Analyzes a SQL file. Returns (edges, table_schemas, metadata)."""
        if not filepath.endswith(".sql"): return [], {}, {}
        try:
            with open(filepath, "r", encoding="utf-8") as f: content = f.read()
        except Exception: return [], {}, {}
        
        dialect = dialect or self.default_dialect
        mocked_sql = self._mock_jinja(content)
        edges, table_schemas, metadata = [], {}, {"operations": [], "column_lineage": [], "scopes": []}
        lhash = self._generate_logic_hash(mocked_sql)
        
        try:
            expression = parse_one(mocked_sql, read=dialect)
            qualified = qualify(expression, schema=schema, validate_qualify_columns=False)
            root_scope = build_scope(qualified)
            
            # 1. CTE Scope Tracking (Phase 2.12)
            for scope in root_scope.traverse():
                if scope.is_cte:
                    cte_name = next((k for k, v in scope.parent.sources.items() if v == scope), "unknown_cte")
                    cte_identity = f"cte:{cte_name}"
                    metadata["scopes"].append({
                        "identity": cte_identity,
                        "name": cte_name,
                        "type": "SQL_SCOPE",
                        "logic_hash": self._generate_logic_hash(scope.expression.sql())
                    })
                    # Source of CTE -> CTE
                    for alias, source in scope.sources.items():
                        if isinstance(source, exp.Table):
                            table_name = source.name.strip('"').strip("'").strip("`")
                            # Normalize dbt refs/sources if needed
                            if table_name.startswith("__dbt_ref_"): table_name = table_name[len("__dbt_ref_"):-2] if table_name.endswith("__") else table_name[len("__dbt_ref_"):]
                            edges.append(LineageEdge(source=table_name, target=cte_identity, type="SQL_INTERNAL", origin_analyzer="sql_lineage", confidence_score=1.0))
                    
                    # CTE -> Parent/Next Scope (placeholder for now, usually consumed by parent query)
                    edges.append(LineageEdge(source=cte_identity, target=identity, type="SQL_SCOPE_FLOW", origin_analyzer="sql_lineage", confidence_score=0.9))

            tables = self._extract_tables(qualified)
            output_columns = self._extract_columns(qualified, root_scope, schema=schema, identity=identity)
            table_schemas[identity] = output_columns
            metadata["column_lineage"] = [{"target": c.name, "sources": c.source_columns} for c in output_columns]
            
            # Operation Detection
            ops = []
            for j in qualified.find_all(exp.Join): ops.append({"type": "JOIN", "join_type": j.args.get("side", "INNER") or "INNER"})
            for g in qualified.find_all(exp.Group): ops.append({"type": "GROUP_BY"})
            for a in qualified.find_all(exp.AggFunc): ops.append({"type": "AGGREGATION", "function": a.__class__.__name__.upper()})
            for w in qualified.find_all(exp.Where): ops.append({"type": "FILTER"})
            for u in qualified.find_all(exp.Union): ops.append({"type": "UNION"})
            seen_ops, unique_ops = set(), []
            for op in ops:
                op_key = json.dumps(op, sort_keys=True)
                if op_key not in seen_ops: unique_ops.append(op); seen_ops.add(op_key)
            metadata["operations"] = unique_ops
            confidence = 1.0
        except Exception:
            patterns = [r"FROM\s+([a-zA-Z0-9_\.]+)", r"JOIN\s+([a-zA-Z0-9_\.]+)"]
            found = set()
            for p in patterns:
                for match in re.finditer(p, mocked_sql, re.IGNORECASE): found.add(match.group(1).strip('"\'`'))
            tables, confidence = list(found), 0.3
            
        for table in tables:
            etype, final_name = "TRANSFORM", table
            if table.lower().startswith("__dbt_ref_"): etype, final_name = "DBT_REF", table[len("__dbt_ref_"):-2] if table.endswith("__") else table[len("__dbt_ref_"):]
            elif table.lower().startswith("__dbt_source_"):
                etype, final_name = "DBT_SOURCE", table[len("__dbt_source_"):]
                if final_name.endswith("__"): final_name = final_name[:-2]
                if "_" in final_name: final_name = final_name.split("_")[-1]
            edges.append(LineageEdge(source=final_name, target=identity, type=etype, origin_analyzer="sql_lineage", confidence_score=confidence, logic_hash=lhash, source_module=identity, line_number=1 if confidence == 1.0 else None))
            
        return edges, table_schemas, metadata
