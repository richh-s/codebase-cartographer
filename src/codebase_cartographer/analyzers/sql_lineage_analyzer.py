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

    def _extract_columns(self, expression, root_scope, schema=None) -> List[ColumnRef]:
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
                return [f"{tname}.{column_name}"]
            
            elif source.__class__.__name__ == "Scope":
                for expr in source.expression.expressions:
                    if expr.alias_or_name == column_name:
                        sources = []
                        cols = list(expr.find_all(exp.Column))
                        if not cols: return [f"{table_alias or 'unknown'}.{column_name}"]
                        for col in cols:
                            sources.extend(resolve_column_source(col.table, col.name, source, depth + 1))
                        return sources
                
                # Star passthrough: search ALL sources of this subquery
                bases = []
                for alias in source.sources:
                    bases.extend(resolve_column_source(alias, column_name, source, depth + 1))
                if bases: return list(dict.fromkeys(bases))
            
            # Step 3: Handle Naked Columns
            if table_alias is None:
                bases = []
                for alias in scope.sources:
                    res = resolve_column_source(alias, column_name, scope, depth + 1)
                    if res: bases.extend(res)
                if bases: return list(dict.fromkeys(bases))
            
            # Step 4: Bubble up to Parent (avoiding CTE self-reference loop)
            if scope.parent:
                # If we are in the root scope, don't bubble
                if scope == root_scope: return [f"{table_alias or 'unknown'}.{column_name}"]
                return resolve_column_source(table_alias, column_name, scope.parent, depth + 1)
                
            prefix = f"{table_alias}." if table_alias else ""
            return [f"{prefix}{column_name}"]

        columns = []
        # Find the top-level projection (the SELECT list of the main query)
        selects = expression.find_all(exp.Select)
        main_select = next(selects, None)
        if main_select:
            for item in main_select.expressions:
                if isinstance(item, exp.Alias):
                    name = item.alias
                else:
                    name = item.alias_or_name
                source_cols = []
                # Handle Star expansions at top level
                if isinstance(item, exp.Star):
                    # For * in the main query, it draws from all sources in root scope
                    for alias in root_scope.sources:
                        source_cols.extend(resolve_column_source(alias, "*", root_scope))
                else:
                    # Request 5: Filter conditional fields in CASE/AGGREGATIONS if they are purely for filtering
                    # We'll use a helper to find "value" columns
                    def find_value_columns(expr):
                        if isinstance(expr, exp.Case):
                            # In CASE, 'then' and 'else' are the value providers
                            vals = []
                            for case in expr.args.get("ifs", []):
                                vals.extend(find_value_columns(case.args.get("true")))
                            if expr.args.get("default"):
                                vals.extend(find_value_columns(expr.args.get("default")))
                            return vals
                        elif isinstance(expr, exp.AggFunc):
                            # In most AggFuncs (SUM, AVG), the first arg is the value
                            # This is a heuristic.
                            return find_value_columns(expr.this)
                        elif isinstance(expr, exp.Column):
                            return [expr]
                        else:
                            # Recurse into all arguments except 'WHEN' conditions
                            cols = []
                            for arg in expr.args.values():
                                if isinstance(arg, list):
                                    for sub in arg: 
                                        if isinstance(sub, exp.Expression):
                                            cols.extend(find_value_columns(sub))
                                elif isinstance(arg, exp.Expression):
                                    cols.extend(find_value_columns(arg))
                            return cols

                    # If it's a numeric aggregate, be selective
                    if any(isinstance(node, (exp.Sum, exp.Avg, exp.Max, exp.Min)) for node in item.find_all(exp.AggFunc)):
                        val_cols = find_value_columns(item)
                    else:
                        val_cols = list(item.find_all(exp.Column))
                        
                    for c in val_cols:
                        resolved = resolve_column_source(c.table, c.name, root_scope)
                        source_cols.extend(resolved)
                
                # Request 3: Ensure result always has a prefix
                source_cols = [s if "." in s else f"unknown.{s}" for s in source_cols]
                
                # Deduplicate sources
                source_cols = list(dict.fromkeys(source_cols))
                
                columns.append(ColumnRef(
                    name=name,
                    source_columns=source_cols,
                    confidence=1.0
                ))
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
        metadata = {
            "operations": [],
            "column_lineage": []
        }
        
        # logic_hash of normalized SQL
        lhash = self._generate_logic_hash(mocked_sql)
        
        try:
            # Sequence: parse -> qualify -> build_scope
            expression = parse_one(mocked_sql, read=dialect)
            qualified = qualify(expression, schema=schema, validate_qualify_columns=False)
            
            # Build scope for table resolution
            root_scope = build_scope(qualified)
            print(f"DEBUG SQL for {identity}: {qualified.sql()}")
            tables = self._extract_tables(qualified)
            
            output_columns = self._extract_columns(qualified, root_scope, schema=schema)
            table_schemas[identity] = output_columns
            confidence = 1.0
            
            # Phase 2.8: Detect structured operations
            ops = []
            for j in qualified.find_all(exp.Join):
                ops.append({
                    "type": "JOIN",
                    "join_type": j.args.get("side", "INNER") or "INNER"
                })
            for g in qualified.find_all(exp.Group):
                ops.append({"type": "GROUP_BY"})
            for a in qualified.find_all(exp.AggFunc):
                ops.append({
                    "type": "AGGREGATION",
                    "function": a.__class__.__name__.upper()
                })
            for w in qualified.find_all(exp.Where):
                ops.append({"type": "FILTER"})
            for u in qualified.find_all(exp.Union):
                ops.append({"type": "UNION"})
            
            # Phase 2.9: Deduplicate operations
            unique_ops = []
            seen_ops = set()
            for op in ops:
                op_key = json.dumps(op, sort_keys=True)
                if op_key not in seen_ops:
                    unique_ops.append(op)
                    seen_ops.add(op_key)
            
            metadata["operations"] = unique_ops
            
            for col in output_columns:
                if col.source_columns:
                    clean_sources = []
                    for s in col.source_columns:
                        s_clean = s
                        if "__dbt_ref_" in s_clean:
                            s_clean = re.sub(r"__dbt_ref_([a-zA-Z0-9_]+)__", r"\1", s_clean)
                        if "__dbt_source_" in s_clean:
                            s_clean = re.sub(r"__dbt_source_([a-zA-Z0-9_]+)_([a-zA-Z0-9_]+)__", r"\1.\2", s_clean)
                        clean_sources.append(s_clean)
                    
                    metadata["column_lineage"].append({
                        "target": col.name,
                        "sources": clean_sources
                    })
        except Exception as e:
            print(f"Fallback triggered for {identity}: {type(e).__name__} - {e}")
            # Fallback (Heuristic)
            patterns = [r"FROM\s+([a-zA-Z0-9_\.]+)", r"JOIN\s+([a-zA-Z0-9_\.]+)"]
            found = set()
            for p in patterns:
                for match in re.finditer(p, mocked_sql, re.IGNORECASE):
                    found.add(match.group(1).strip('"\'`'))
            tables = list(found)
            confidence = 0.3

        # Apply edges to all discovered tables
        for table in tables:
            etype = "TRANSFORM"
            final_name = table
            
            # Manual resolution of mock names (applies to both parsed and fallback)
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
