import re
import yaml
from typing import List
from codebase_cartographer.models.lineage import LineageEdge

class AirflowDagParser:
    """Parses Airflow DAGs (Python) for virtual task dependencies (>>)."""
    
    def can_handle(self, filepath: str) -> bool:
        if not filepath.endswith(".py"): return False
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read(2048) # Just a peek
            return ("DAG" in content or "airflow" in content.lower()) and ">>" in content
        except Exception: return False

    def parse(self, filepath: str, identity: str) -> List[LineageEdge]:
        edges = []
        try:
             with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
             
             # Regex for basic task dependencies: task_a >> task_b
             matches = re.finditer(r"([a-zA-Z0-9_]+)\s*>>\s*([a-zA-Z0-9_]+)", content)
             for match in matches:
                 edges.append(LineageEdge(
                     source=match.group(1),
                     target=match.group(2),
                     type="CONFIG_DEPENDENCY",
                     origin_analyzer="dag_config",
                     confidence_score=0.8,
                     source_module=identity
                 ))
                 
             # Detect set_upstream/set_downstream
             matches = re.finditer(r"([a-zA-Z0-9_]+)\.set_downstream\(\s*([a-zA-Z0-9_]+)\s*\)", content)
             for match in matches:
                 edges.append(LineageEdge(
                     source=match.group(1),
                     target=match.group(2),
                     type="CONFIG_DEPENDENCY",
                     origin_analyzer="dag_config",
                     confidence_score=0.8,
                     source_module=identity
                 ))
        except Exception: pass
        return edges

class DbtConfigParser:
    """Parses dbt schema.yml for metadata-based dependencies and sources."""
    
    def can_handle(self, filepath: str) -> bool:
        return filepath.endswith(".yml") or filepath.endswith(".yaml")

    def parse(self, filepath: str, identity: str) -> List[LineageEdge]:
        edges = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            
            if not config: return []
                
            # 1. Models dependencies (dbt_refs usually handled by SQL, but meta-lineage here)
            for model in config.get("models", []):
                model_name = model.get("name")
                if not model_name: continue
                # We can add more metadata-based edges here if needed
                pass
                
            # 2. Sources registration
            # sources:
            #   - name: raw_orders
            #     tables:
            #       - name: orders
            if "sources" in config:
                for src in config["sources"]:
                    src_name = src.get("name")
                    for table in src.get("tables", []):
                        table_name = table.get("name")
                        if src_name and table_name:
                            # Create a metadata dependency edge (identity -> source)
                            # This helps HydrologistAgent discover the source DataNode
                            edges.append(LineageEdge(
                                source=identity,
                                target=f"{src_name}.{table_name}",
                                type="DBT_SOURCE",
                                origin_analyzer="dag_config",
                                confidence_score=1.0,
                                source_module=identity
                            ))
        except Exception: pass
        return edges
