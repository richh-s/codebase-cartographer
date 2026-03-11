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
            return "DAG" in content and ">>" in content
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
                     confidence_score=0.7,
                     source_module=identity
                 ))
        except Exception: pass
        return edges

class DbtConfigParser:
    """Parses dbt schema.yml for metadata-based dependencies."""
    
    def can_handle(self, filepath: str) -> bool:
        return filepath.endswith(".yml") or filepath.endswith(".yaml")

    def parse(self, filepath: str, identity: str) -> List[LineageEdge]:
        edges = []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            
            if not config or "models" not in config:
                return []
                
            for model in config.get("models", []):
                model_name = model.get("name")
                if not model_name: continue
                
                # If a model describes another, it's a metadata dependency
                # We already handle this in Phase 1, but here we can add CONFIG_DEPENDENCY
                # if there are specific tests or properties.
                pass
        except Exception: pass
        return edges
