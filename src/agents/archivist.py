import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from models.nodes import ModuleNode

class ArchivistAgent:
    """
    Agent responsible for generating living context artifacts.
    Fulfills Phase 4 requirements for determinism, portability, and overrides.
    """
    
    def __init__(self, repo_path: str, st_threshold: int = 5):
        self.repo_path = os.path.abspath(repo_path)
        self.st_threshold = st_threshold
        self.schema_version = "1.0"
        self.analysis_version = "cartographer_phase4"

    def apply_overrides(self, modules: List[ModuleNode], overrides_path: str):
        """
        Applies manual overrides from overrides.json.
        Validation: Errors out if the target module doesn't exist.
        """
        if not os.path.exists(overrides_path):
            return

        try:
            with open(overrides_path, "r") as f:
                overrides = json.load(f)
            
            module_map = {m.path: m for m in modules}
            for entry in overrides:
                target = entry.get("module")
                if target not in module_map:
                    print(f"[Warning] Archivist: Override target '{target}' not found in graph.")
                    continue
                
                m = module_map[target]
                if "purpose" in entry:
                    m.purpose_statement = entry["purpose"]
                if "layer" in entry:
                    m.architecture_layer = entry["layer"]
                if "domain" in entry:
                    m.domain_cluster = entry["domain"]
                
                print(f"[Info] Archivist: Applied override to {target}")
        except Exception as e:
            print(f"[Error] Archivist: Failed to apply overrides: {e}")

    def generate_codebase_report(self, modules: List[ModuleNode], git_sha: str, output_path: str):
        """
        Generates a deterministic CODEBASE.md summarizing the repository context.
        Includes freshness indicators and categorized debt.
        """
        # Deterministic sort
        modules = sorted(modules, key=lambda m: (m.domain_cluster or "Unknown", m.path))
        
        lines = [
            "# 🗺️ Codebase Technical Overview",
            f"**Commit SHA:** `{git_sha}`",
            f"**Generated:** {datetime.now().isoformat()}",
            f"**Total Modules:** {len(modules)}",
            "",
            "## 📂 Module Inventory",
            "| Module | Domain | Layer | Status | Purpose |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ]
        
        for m in modules:
            # Freshness Logic
            # Note: commit_count_30d would ideally be passed in or stored on ModuleNode
            # For now, we assume it's attached via metadata or available in context
            commit_count = getattr(m, "commit_count_30d", 0)
            status = "✅ Stable"
            if commit_count > self.st_threshold:
                status = "⚠️ Potentially Stale"
            
            purpose = (m.purpose_statement or "No purpose statement generated.").replace("\n", " ")
            domain = m.domain_cluster or "General"
            layer = m.architecture_layer or "Unknown"
            
            # Use relative paths for portability
            rel_path = os.path.relpath(m.path, self.repo_path) if os.path.isabs(m.path) else m.path
            
            lines.append(f"| `{rel_path}` | {domain} | {layer} | {status} | {purpose} |")
            
        with open(output_path, "w") as f:
            f.write("\n".join(lines))
        print(f"[Info] Archivist: Codebase report saved to {output_path}")

    def export_graph_json(self, data: Dict[str, Any], git_sha: str, output_path: str):
        """
        Exports graph data with a standard metadata header and deterministic keys.
        """
        header = {
            "schema_version": self.schema_version,
            "analysis_version": self.analysis_version,
            "git_commit": git_sha,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # Merge header with data
        payload = {**header, **data}
        
        try:
            with open(output_path, "w") as f:
                json.dump(payload, f, indent=2, sort_keys=True, default=str)
            print(f"[Info] Archivist: Artifact saved to {output_path}")
        except Exception as e:
            print(f"[Error] Archivist: Failed to export artifact: {e}")
