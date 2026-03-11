import re
import json
import hashlib
import sqlglot
from sqlglot import exp, parse_one
from sqlglot.optimizer.qualify import qualify
from sqlglot.optimizer.scope import build_scope
from typing import List, Optional, Dict, Tuple, Any
from codebase_cartographer.models.lineage import LineageEdge, ColumnRef

class SQLLineageAnalyzer:
    """Uses sqlglot to extract lineage from SQL and dbt models with Phase 2.5 refinements."""
    
    def __init__(self, default_dialect: str = "duckdb"):
        self.default_dialect = default_dialect

    def _generate_logic_hash(self, sql: str) -> str:
        """Generates a stable, whitespace-insensitive hash for SQL content."""
        # Normalize: strip dbt specific IDs which change between builds
        normalized = re.sub(r"__dbt_ref_([a-zA-Z0-9_]+)__", r"\1", sql)
        normalized = re.sub(r"__dbt_source_([a-zA-Z0-9_]+)_([a-zA-Z0-9_]+)__", r"\1.\2", normalized)
        # Lowercase and collapse whitespace
        normalized = " ".join(normalized.lower().split()).strip()
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]

    def _mock_jinja(self, sql: str) -> str:
        """Mocks dbt Jinja tags into parseable SQL identifiers."""
        # Replace ref()
        sql = re.sub(r"\{\{\s*ref\s*\(\s*['\"]([^'\"]+)['\"]\s*\)\s*\}\}", r"__dbt_ref_\1__", sql)
        # Replace source()
        sql = re.sub(r"\{\{\s*source\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)\s*\}\}", r"__dbt_source_\1_\2__", sql)
        # Strip other {{ ... }} tags
        sql = re.sub(r"\{\{.*?\}\}", " ", sql)
        # Strip {% ... %} tags
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
        def resolve_column_source(table_alias: str, column_name: str, scope, depth=0) -> List[str]:
            if depth > 10: return [] # Safety break
            
            if not scope: 
                prefix = f"{table_alias}." if table_alias else ""
                return [f"{prefix}{column_name}"]
            
            # Step 1: Direct Schema Match (Physical Tables / Mocked Refs)
            if schema and table_alias and table_alias in schema:
                if column_name.lower() in schema[table_alias]:
                    tname = table_alias
                    if tname.startswith("__dbt_ref_"):
                        tname = tname[len("__dbt_ref_"):-2] if tname.endswith("__") else tname[len("__dbt_ref_"):]
                    return [f"{tname}.{column_name}"]
            
            # Step 2: Resolve Alias in Current Scope
            source = scope.sources.get(table_alias)
            
            if isinstance(source, exp.Table):
                tname = source.name.strip('"').strip("'").strip("`")
                if tname.startswith("__dbt_ref_"):
                    tname = tname[len("__dbt_ref_"):-2] if tname.endswith("__") else tname[len("__dbt_ref_"):]
                elif tname.startswith("__dbt_source_"):
                    tname = tname[len("__dbt_source_"):]
                    if tname.endswith("__"): tname = tname[:-2]
                    # Check for jaffle_shop_orders and similar
                    if "_" in tname:
                        parts = tname.split("_")
                        # Heuristic: if it's jaffle_shop_orders, try to find raw_orders or orders
                        # We'll return BOTH options if we're not sure, or better: 
                        # just return the table name and let Hydrologist resolve it.
                        tname = parts[-1]
                return [f"{tname}.{column_name}"]
            
            elif source.__class__.__name__ == "Scope":
                for expr in source.expression.expressions:
                    if expr.alias_or_name == column_name:
                        sources = []
                        # Phase 2.12: Use find_value_columns here too!
                        val_cols = find_value_columns(expr)
                        if not val_cols: 
                            # If no value cols found, could be a literal or *
                            # if it's exactly the alias, maybe it's a passthrough we missed
                            return [f"{table_alias or 'unknown'}.{column_name}"]
                        
                        for col in val_cols:
                            sources.extend(resolve_column_source(col.table, col.name, source, depth + 1))
                        return list(dict.fromkeys(sources))
                
                # Star passthrough
                bases = []
                for alias in source.sources:
                    bases.extend(resolve_column_source(alias, column_name, source, depth + 1))
                if bases: return list(dict.fromkeys(bases))
            
            # Step 3: Handle Naked Columns
            if table_alias is None:
                bases = []
                for alias in scope.sources:
                    res = resolve_column_source(alias, column_name, scope, depth + 1)
                    if res:
                        source = scope.sources.get(alias)
                        if isinstance(source, exp.Table):
                            bases.extend([b if "." in b else f"{alias}.{b}" for b in res])
                        else:
                            bases.extend(res)
                if bases: return list(dict.fromkeys(bases))
            
            # Step 4: Bubble up to Parent
            if scope.parent:
                if scope == root_scope: return [f"{table_alias or 'unknown'}.{column_name}"]
                return resolve_column_source(table_alias, column_name, scope.parent, depth + 1)
                
            prefix = f"{table_alias}." if table_alias else ""
            return [f"{prefix}{column_name}"]

        def find_value_columns(expr):
            if isinstance(expr, exp.Case):
                vals = []
                for case in expr.args.get("ifs", []):
                    # strictly follow only the THEN branch
                    vals.extend(find_value_columns(case.args.get("true")))
                if expr.args.get("default"):
                    vals.extend(find_value_columns(expr.args.get("default")))
                return vals
            elif isinstance(expr, exp.AggFunc):
                return find_value_columns(expr.this)
            elif isinstance(expr, exp.Column):
                return [expr]
            elif isinstance(expr, exp.Alias):
                return find_value_columns(expr.this)
            elif isinstance(expr, (exp.Literal, exp.Null)):
                return []
            else:
                cols = []
                for arg_key, arg in expr.args.items():
                    if arg_key in ["on", "where", "having"]: continue # Only values
                    if isinstance(arg, list):
                        for sub in arg: 
                            if isinstance(sub, exp.Expression):
                                cols.extend(find_value_columns(sub))
                    elif isinstance(arg, exp.Expression):
                        cols.extend(find_value_columns(arg))
                return cols

        columns = []
        selects = expression.find_all(exp.Select)
        main_select = next(selects, None)
        if main_select:
            for item in main_select.expressions:
                if isinstance(item, exp.Alias):
                    name = item.alias
                else:
                    name = item.alias_or_name
                
                source_cols = []
                if isinstance(item, exp.Star):
                    for alias in root_scope.sources:
                        source_cols.extend(resolve_column_source(alias, "*", root_scope))
                else:
                    # Request 5: Precise CASE filtering
                    if any(isinstance(node, (exp.Sum, exp.Avg, exp.Max, exp.Min)) for node in item.find_all(exp.AggFunc)):
                        val_cols = find_value_columns(item)
                        if not val_cols: val_cols = list(item.find_all(exp.Column))
                    else:
                        val_cols = list(item.find_all(exp.Column))
                    
                    for c in val_cols:
                        resolved = resolve_column_source(c.table, c.name, root_scope)
                        source_cols.extend(resolved)
                
                # Resolve prefixes and filter "unknown."
                final_sources = set()
                # Phase 2.14: Pre-calculate all internal aliases in the whole model
                model_aliases = set()
                for scope_node in root_scope.traverse():
                    for alias, source in scope_node.sources.items():
                        if source.__class__.__name__ == "Scope":
                            model_aliases.add(alias.lower())
                
                dbt_keywords = {"source", "ref", "renamed", "stg", "final", "base", "source", "renamed"} | model_aliases

                for s in source_cols:
                    if "." in s:
                        prefix, col_res = s.split(".", 1)
                        if prefix.lower() not in dbt_keywords and not s.startswith("unknown."):
                            final_sources.add(s)
                            continue
                            
                        # Peeling back: If prefix is internal, try to find its actual source
                        current_prefix = prefix
                        peeled = False
                        for _ in range(10): # Deep recursion
                            # Find the source node by searching all scopes in the model
                            target_node = None
                            for sc in root_scope.traverse():
                                if current_prefix.lower() in {k.lower() for k in sc.sources}:
                                    target_node = sc.sources.get(current_prefix) or \
                                                  {k.lower(): v for k, v in sc.sources.items()}.get(current_prefix.lower())
                                    if target_node: break
                            
                            if target_node:
                                if target_node.__class__.__name__ == "Scope":
                                    # If this CTE wraps a single table, jump to it
                                    tables = [s for s in target_node.sources.values() if isinstance(s, exp.Table)]
                                    if tables:
                                        target_node = tables[0]
                                    else:
                                        # Try to find the next alias in the chain
                                        valid_subs = {k: v for k, v in target_node.sources.items() if not k.startswith("_")}
                                        if valid_subs:
                                            next_alias = list(valid_subs.keys())[0]
                                            if next_alias.lower() != current_prefix.lower():
                                                current_prefix = next_alias
                                                continue
                                            else: break
                                        else: break
                                
                                if isinstance(target_node, exp.Table):
                                    tname = target_node.name.strip('"').strip("'").strip("`")
                                    # Normalize
                                    if tname.startswith("__dbt_ref_"):
                                        tname = tname[len("__dbt_ref_"):-2] if tname.endswith("__") else tname[len("__dbt_ref_"):]
                                    elif tname.startswith("__dbt_source_"):
                                        tname = tname[len("__dbt_source_"):]
                                        if tname.endswith("__"): tname = tname[:-2]
                                        if "_" in tname: tname = tname.split("_")[-1]
                                    final_sources.add(f"{tname}.{col_res}")
                                    peeled = True
                                    break
                                else: break
                            else: break
                        
                        if not peeled:
                            # Fallback to aggressive but cautious search
                            valid_sources = {k: v for k, v in root_scope.sources.items() if not k.startswith("_")}
                            if not valid_sources: valid_sources = root_scope.sources
                            filtered_sources = {k: v for k, v in valid_sources.items() if k.lower() not in dbt_keywords}
                            best_sources = filtered_sources if filtered_sources else valid_sources
                            
                            if len(best_sources) >= 1:
                                alias = list(best_sources.keys())[0]
                                source_node = best_sources[alias]
                                tname = alias
                                if isinstance(source_node, exp.Table):
                                    tname = source_node.name.strip('"').strip("'").strip("`")
                                if tname.startswith("__dbt_ref_"): tname = tname[len("__dbt_ref_"):-2] if tname.endswith("__") else tname[len("__dbt_ref_"):]
                                elif tname.startswith("__dbt_source_"):
                                    tname = tname[len("__dbt_source_"):]
                                    if tname.endswith("__"): tname = tname[:-2]
                                    if "_" in tname: tname = tname.split("_")[-1]
                                final_sources.add(f"{tname}.{col_res}")
                            else:
                                final_sources.add(f"unknown.{col_res}")
                    else:
                        # Naked column - use aggressive search
                        valid_sources = {k: v for k, v in root_scope.sources.items() if not k.startswith("_")}
                        filtered_sources = {k: v for k, v in valid_sources.items() if k.lower() not in dbt_keywords}
                        best_sources = filtered_sources if filtered_sources else valid_sources
                        if len(best_sources) >= 1:
                            alias = list(best_sources.keys())[0]
                            source_node = best_sources[alias]
                            tname = alias
                            if isinstance(source_node, exp.Table):
                                tname = source_node.name.strip('"').strip("'").strip("`")
                            if tname.startswith("__dbt_ref_"): tname = tname[len("__dbt_ref_"):-2] if tname.endswith("__") else tname[len("__dbt_ref_"):]
                            elif tname.startswith("__dbt_source_"):
                                tname = tname[len("__dbt_source_"):]
                                if tname.endswith("__"): tname = tname[:-2]
                                if "_" in tname: tname = tname.split("_")[-1]
                            final_sources.add(f"{tname}.{s}")
                        else:
                            final_sources.add(f"unknown.{s}")
                
                columns.append(ColumnRef(
                    name=name,
                    source_columns=sorted(list(final_sources)),
                    confidence=1.0
                ))
            
            # Deterministic Ordering & Deduplication
            seen_targets = {}
            for c in columns:
                if c.name not in seen_targets:
                    seen_targets[c.name] = c
                else:
                    combined = sorted(list(dict.fromkeys(seen_targets[c.name].source_columns + c.source_columns)))
                    seen_targets[c.name].source_columns = combined
            columns = sorted(seen_targets.values(), key=lambda x: x.name)

        return columns

    def analyze(self, filepath: str, identity: str, dialect: Optional[str] = None, schema: Optional[Dict] = None) -> Tuple[List[LineageEdge], Dict[str, List[ColumnRef]], Dict[str, Any]]:
        """Analyzes a SQL file. Returns (edges, table_schemas, metadata)."""
        if not filepath.endswith(".sql"):
            return [], {}, {}
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return [], {}, {}

        dialect = dialect or self.default_dialect
        mocked_sql = self._mock_jinja(content)
        edges = []
        table_schemas = {}
        metadata = {"operations": [], "column_lineage": []}
        lhash = self._generate_logic_hash(mocked_sql)
        
        try:
            expression = parse_one(mocked_sql, read=dialect)
            qualified = qualify(expression, schema=schema, validate_qualify_columns=False)
            root_scope = build_scope(qualified)
            tables = self._extract_tables(qualified)
            
            output_columns = self._extract_columns(qualified, root_scope, schema=schema, identity=identity)
            table_schemas[identity] = output_columns
            metadata["column_lineage"] = [{"target": c.name, "sources": c.source_columns} for c in output_columns]
            confidence = 1.0
            
            ops = []
            for j in qualified.find_all(exp.Join):
                ops.append({"type": "JOIN", "join_type": j.args.get("side", "INNER") or "INNER"})
            for g in qualified.find_all(exp.Group):
                ops.append({"type": "GROUP_BY"})
            for a in qualified.find_all(exp.AggFunc):
                ops.append({"type": "AGGREGATION", "function": a.__class__.__name__.upper()})
            for w in qualified.find_all(exp.Where):
                ops.append({"type": "FILTER"})
            for u in qualified.find_all(exp.Union):
                ops.append({"type": "UNION"})
            
            seen_ops = set()
            unique_ops = []
            for op in ops:
                op_key = json.dumps(op, sort_keys=True)
                if op_key not in seen_ops:
                    unique_ops.append(op)
                    seen_ops.add(op_key)
            metadata["operations"] = unique_ops
            
        except Exception as e:
            print(f"Fallback triggered for {identity}: {type(e).__name__} - {e}")
            patterns = [r"FROM\s+([a-zA-Z0-9_\.]+)", r"JOIN\s+([a-zA-Z0-9_\.]+)"]
            found = set()
            for p in patterns:
                for match in re.finditer(p, mocked_sql, re.IGNORECASE):
                    found.add(match.group(1).strip('"\'`'))
            tables = list(found)
            confidence = 0.3

        for table in tables:
            etype = "TRANSFORM"
            final_name = table
            if table.lower().startswith("__dbt_ref_"):
                etype = "DBT_REF"
                final_name = table[len("__dbt_ref_"):]
                if final_name.endswith("__"): final_name = final_name[:-2]
            elif table.lower().startswith("__dbt_source_"):
                etype = "DBT_SOURCE"
                final_name = table[len("__dbt_source_"):]
                if final_name.endswith("__"): final_name = final_name[:-2]
            
            edges.append(LineageEdge(
                source=final_name,
                target=identity,
                type=etype,
                origin_analyzer="sql_lineage",
                confidence_score=confidence,
                logic_hash=lhash,
                source_module=identity,
                line_number=1 if confidence == 1.0 else None
            ))
        return edges, table_schemas, metadata
