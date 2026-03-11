import os
import json
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from codebase_cartographer.analyzers.python_dataflow_analyzer import PythonDataFlowAnalyzer
from codebase_cartographer.analyzers.sql_lineage_analyzer import SQLLineageAnalyzer
from codebase_cartographer.analyzers.dag_config_analyzer import DAGConfigAnalyzer
from codebase_cartographer.analyzers.dag_parsers.plugins import AirflowDagParser, DbtConfigParser
from codebase_cartographer.utils.identity_resolver import IdentityResolver
from codebase_cartographer.graph.lineage_graph import LineageGraph
from codebase_cartographer.models.lineage import DataNode, LineageEdge, TransformationNode, DatasetRole

class HydrologistAgent:
    """Coordinates Phase 2.6: Advanced multi-modal data lineage extraction."""
    
    def __init__(self, target_dir: str):
        self.target_dir = target_dir
        self.python_analyzer = PythonDataFlowAnalyzer()
        self.sql_analyzer = SQLLineageAnalyzer()
        self.dag_analyzer = DAGConfigAnalyzer()
        self.dag_analyzer.register_parser(AirflowDagParser())
        self.dag_analyzer.register_parser(DbtConfigParser())
        
        # Phase 2.6 refinement: IdentityResolver replaces basic Canonicalization
        self.identity_resolver = IdentityResolver()
        self.lineage_graph = LineageGraph()
        
        self.discovered_schemas: Dict[str, List[Any]] = {}
        self.inferred_schemas: Dict[str, set] = {}
        self.dataset_to_system: Dict[str, str] = {}
        self.graph_version = self._get_git_version()
        
    def _get_git_version(self) -> str:
        try:
            return "git:" + subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"], 
                cwd=self.target_dir, text=True, stderr=subprocess.DEVNULL
            ).strip()
        except Exception:
            return "unknown"

    def _is_module(self, identity: str) -> bool:
        """Heuristic to distinguish code modules from datasets."""
        return identity.endswith((".py", ".sql", ".yml", ".yaml"))

    def _is_dataset(self, identity: str) -> bool:
        """Heuristic to distinguish datasets from code modules."""
        if ":" in identity: return True
        if self._is_module(identity): return False
        if "/" not in identity: return True 
        return True

    def _calculate_dynamic_confidence(self, base_conf: float, edge: LineageEdge) -> float:
        """Phase 2.6: Confidence degrades with missing context or multiple heuristics."""
        completeness_factor = 1.0
        if not edge.source_module: completeness_factor *= 0.8
        if "unknown" in edge.source or "unknown" in edge.target: completeness_factor *= 0.7
        return round(base_conf * completeness_factor, 2)

    def run(self, output_json: str = ".cartography/lineage.json"):
        """
        Traverses the codebase and extracts lineage edges with Phase 2.6 refinements.
        """
        all_edges: List[LineageEdge] = []
        
        # Pass 0: Constants Discovery
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "rb") as f:
                            source_bytes = f.read()
                        tree = self.python_analyzer.parser.parse(source_bytes)
                        local_consts = self.python_analyzer._extract_constants(tree.root_node, source_bytes)
                        self.shared_constants.update(local_consts)
                    except Exception:
                        continue

        # Pass 1: Extraction
        sql_files = []
        other_files = []
        for root, dirs, files in os.walk(self.target_dir):
            for file in files:
                filepath = os.path.join(root, file)
                if file.endswith(".sql"):
                    sql_files.append((root, file, filepath))
                else:
                    other_files.append((root, file, filepath))
        
        # Sort SQL files: staging/base/source first, then by depth descending
        sql_files.sort(key=lambda x: (
            not any(p in x[2].lower() for p in ["staging", "stg", "base", "src", "seed"]),
            -x[2].count(os.sep), 
            x[1]
        ))
        
        for root, file, filepath in sql_files + other_files:
            rel_path = os.path.relpath(filepath, self.target_dir)
            identity = rel_path
                
            if file.endswith(".py"):
                edges, _ = self.python_analyzer.analyze(filepath, identity, self.shared_constants)
                all_edges.extend(edges)
                dag_edges = self.dag_analyzer.analyze(filepath, identity)
                all_edges.extend(dag_edges)
            
            elif file.endswith(".sql"):
                # Phase 2.10: Build a schema map for sqlglot qualification
                sqlglot_schema = {}
                for canon_name, col_refs in self.discovered_schemas.items():
                    cols = {c.name.lower(): "INT" for c in col_refs}
                    sqlglot_schema[canon_name] = cols
                    # Map mocked dbt references
                    sqlglot_schema[f"__dbt_ref_{canon_name}__"] = cols
                
                for canon_name, col_names in self.inferred_schemas.items():
                    cols = {c.lower(): "INT" for c in col_names}
                    if canon_name not in sqlglot_schema:
                        sqlglot_schema[canon_name] = cols
                    if f"__dbt_ref_{canon_name}__" not in sqlglot_schema:
                        sqlglot_schema[f"__dbt_ref_{canon_name}__"] = cols
                    # Also handle potential dbt source format (simplified)
                    sqlglot_schema[f"__dbt_source_{canon_name}__"] = cols

                edges, schemas, metadata = self.sql_analyzer.analyze(
                    filepath, identity, schema=sqlglot_schema
                )
                all_edges.extend(edges)
                
                # Create a TransformationNode for the SQL model
                trans_node = TransformationNode(
                    identity=identity,
                    name=os.path.basename(file),
                    type="DBT_MODEL",
                    logic_hash=edges[0].logic_hash if edges else "unknown",
                    operations=metadata.get("operations", []),
                    column_lineage=metadata.get("column_lineage", [])
                )
                self.lineage_graph.add_transformation_node(trans_node)
                
                # Link module to product
                product_raw = os.path.splitext(os.path.basename(file))[0]
                canon_product = self.identity_resolver.resolve(product_raw, "dbt")
                self.dataset_to_system[canon_product] = "dbt"
                
                # Phase 2.10 Restore: Explicit product edge
                all_edges.append(LineageEdge(
                    source=identity,
                    target=product_raw,
                    type="SQL_PRODUCT",
                    origin_analyzer="hydrologist",
                    confidence_score=1.0,
                    source_module=identity
                ))
                
                if identity in schemas:
                    self.discovered_schemas[canon_product] = schemas[identity]
                    print(f"DISCOVERED SCHEMA for {canon_product}: {[c.name for c in schemas[identity]]}")
                
                # Phase 2.8/2.9: Schema Inference for Sources
                for target_table, cols in schemas.items():
                    for col in cols:
                        for sc in col.source_columns:
                            parts = sc.split(".")
                            if len(parts) >= 2:
                                # Canonicalize the base_table name
                                raw_base = parts[0]
                                canon_base = self.identity_resolver.resolve(raw_base, "unknown")
                                col_name = parts[1].lower() # Deduplicate via lowercasing
                                self.inferred_schemas.setdefault(canon_base, set()).add(col_name)
            
            elif file.endswith(".yml") or file.endswith(".yaml"):
                edges = self.dag_analyzer.analyze(filepath, identity)
                all_edges.extend(edges)
            
            # Phase 2.9: Seed Detection
            elif "/seeds/" in filepath and file.endswith(".csv"):
                name_raw = os.path.splitext(file)[0]
                canon_seed = self.identity_resolver.resolve(name_raw, "dbt")
                self.dataset_to_system[canon_seed] = "dbt"

        # Pass 2: Identity Resolution & Topology Refinement
        for edge in all_edges:
            # 1. Resolve Dataset Identities
            for node_id in [edge.source, edge.target]:
                if self._is_dataset(node_id):
                    ns, raw = (node_id.split(":", 1) if ":" in node_id else ("unknown", node_id))
                    canon = self.identity_resolver.resolve(raw, ns)
                    
                    if node_id == edge.source: edge.source = canon
                    else: edge.target = canon
                    
                    if canon not in self.lineage_graph.data_nodes:
                        # Phase 2.6/2.7/2.9/2.10: Enrich DataNode metadata
                        system = self.dataset_to_system.get(canon, ns)
                        if system == "unknown":
                            if "s3://" in raw: system = "s3"
                            elif "gs://" in raw: system = "gcs"
                            elif "snowflake://" in raw: system = "snowflake"
                            elif "postgres://" in raw: system = "postgres"
                            elif "bigquery." in raw: system = "bigquery"
                            elif ".parquet" in raw: system = "parquet"
                            elif ".csv" in raw: system = "csv"
                            
                        # Phase 2.10 Refinement: Be careful with system "dbt"
                        # Only tag as dbt if it's actually produced by a sql file in this repo
                        if raw.endswith(".sql"):
                            system = "dbt"
                        elif canon in self.discovered_schemas:
                            system = "dbt"
                            
                        # If it's a raw source, it shouldn't be "dbt" unless explicitly marked
                        if "raw_" in raw.lower() and canon not in self.discovered_schemas:
                            system = "warehouse" # Fallback for jaffle shop / generic SQL warehouse
                            
                        # Namespace mapping
                        if ns != "unknown":
                            system = ns
                        
                        env = "production" # Default
                        raw_lower = raw.lower()
                        if "dev" in raw_lower: env = "development"
                        elif "qa" in raw_lower: env = "qa"
                        elif "staging" in raw_lower or "stg" in raw_lower: env = "staging"
                        
                        # Phase 2.7: Heuristic dataset typing
                        dataset_type = "object_storage" if system in ["s3", "gcs"] else "database_table"
                        columns = self.discovered_schemas.get(canon, [])
                        confidence = 1.0 if columns else 0.5
                        
                        # Phase 2.8: Schema inference integration
                        if not columns:
                            # Try exact match or name-only match
                            raw_name_key = self.identity_resolver.resolve(raw, "unknown")
                            if raw_name_key in self.inferred_schemas:
                                from codebase_cartographer.models.lineage import ColumnRef
                                columns = [ColumnRef(name=c, confidence=0.7) for c in self.inferred_schemas[raw_name_key]]
                                confidence = 0.7
                            elif canon in self.inferred_schemas:
                                from codebase_cartographer.models.lineage import ColumnRef
                                columns = [ColumnRef(name=c, confidence=0.7) for c in self.inferred_schemas[canon]]
                                confidence = 0.7
                        
                        if "raw_" in raw_lower:
                            dataset_type = "source_table"
                            confidence = 0.9
                        elif "stg_" in raw:
                            dataset_type = "staging_table"
                            confidence = 0.9
                        elif "fct_" in raw:
                            dataset_type = "fact_table"
                            confidence = 0.9
                        elif "dim_" in raw:
                            dataset_type = "dimension_table"
                            confidence = 0.9
                        
                        identity_info = self.identity_resolver.identities.get(canon)
                        
                        self.lineage_graph.add_data_node(DataNode(
                            identity=canon,
                            name=raw,
                            canonical_name=canon,
                            namespace=ns,
                            system=system,
                            environment=env,
                            type=dataset_type,
                            database=identity_info.database if identity_info else None,
                            schema_=identity_info.schema_ if identity_info else None,
                            table=identity_info.table if identity_info else None,
                            columns=columns,
                            version=self.graph_version,
                            timestamp=datetime.now(),
                            dataset_type_confidence=confidence
                        ))
            
            # 2. Inject Transformation Nodes for code-data boundaries
            # WRITE: Code -> Data
            if self._is_module(edge.source) and self._is_dataset(edge.target):
                if edge.source not in self.lineage_graph.transformation_nodes:
                    self.lineage_graph.add_transformation_node(TransformationNode(
                        identity=edge.source,
                        name=os.path.basename(edge.source),
                        type="PYTHON_SCRIPT" if edge.source.endswith(".py") else "DBT_MODEL",
                        logic_hash=edge.logic_hash or "unknown",
                        environment="production"
                    ))
            
            # READ: Data -> Code
            if self._is_dataset(edge.source) and self._is_module(edge.target):
                if edge.target not in self.lineage_graph.transformation_nodes:
                    self.lineage_graph.add_transformation_node(TransformationNode(
                        identity=edge.target,
                        name=os.path.basename(edge.target),
                        type="PYTHON_SCRIPT" if edge.target.endswith(".py") else "DBT_MODEL",
                        logic_hash=edge.logic_hash or "unknown",
                        environment="production"
                    ))
            
            # 3. Dynamic Confidence
            edge.confidence_score = self._calculate_dynamic_confidence(edge.confidence_score, edge)
            self.lineage_graph.add_lineage_edge(edge)

        # Pass 3: Intelligence
        self.lineage_graph.assign_roles()
        
        # Phase 2.6: Override roles based on intent heuristics
        for node in self.lineage_graph.data_nodes.values():
            if "raw" in node.name.lower() or "source" in node.name.lower():
                node.role = DatasetRole.SOURCE
            elif "report" in node.name.lower() or "dashboard" in node.name.lower() or "export" in node.name.lower():
                node.role = DatasetRole.TERMINAL

        self.lineage_graph.compute_importance({}) 

        # Final Export
        out_path = os.path.join(self.target_dir, output_json)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        
        with open(out_path, "w") as f:
            data = {
                "version": self.graph_version,
                "timestamp": datetime.now().isoformat(),
                "nodes": {
                    "data": [n.model_dump() for n in self.lineage_graph.data_nodes.values()],
                    "transformations": [n.model_dump() for n in self.lineage_graph.transformation_nodes.values()]
                },
                "edges": [self.lineage_graph.graph.edges[u, v] for u, v in self.lineage_graph.graph.edges()],
                "health": self.lineage_graph.get_health_report(),
                "warnings": self.lineage_graph.validate_integrity(),
        # Pass 3: Schema Completion for Sources
        for node in self.lineage_graph.data_nodes.values():
            if node.role == "SOURCE" and not node.columns:
                if node.identity in self.inferred_schemas:
                    from codebase_cartographer.models.lineage import ColumnRef
                    node.columns = [ColumnRef(name=c, confidence=0.7) for c in sorted(list(self.inferred_schemas[node.identity]))]
                else:
                    # Try a name-only match if FQDN didn't hit
                    raw_name = node.identity.split(":")[-1] if ":" in node.identity else node.identity
                    if raw_name in self.inferred_schemas:
                        from codebase_cartographer.models.lineage import ColumnRef
                        node.columns = [ColumnRef(name=c, confidence=0.6) for c in sorted(list(self.inferred_schemas[raw_name]))]

        # Finalize and Save
        summary = self.lineage_graph.get_summary()
                "mermaid": self.lineage_graph.to_mermaid()
            }
            json.dump(data, f, indent=2, default=str)
            
        return out_path
