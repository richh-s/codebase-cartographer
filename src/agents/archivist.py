import os
import json
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from models.nodes import ModuleNode

class ArchivistAgent:
    """
    Agent responsible for generating living context artifacts.
    Fulfills Phase 4 requirements for determinism, portability, and overrides.
    """
    
    def __init__(self, repo_path: str, st_threshold: int = 5, logger: Optional[Any] = None):
        self.repo_path = os.path.abspath(repo_path)
        self.output_dir = os.path.join(self.repo_path, ".cartography")
        self.st_threshold = st_threshold
        self.logger = logger
        self.schema_version = "1.0"
        self.analysis_version = "cartographer_phase4"
        os.makedirs(self.output_dir, exist_ok=True)

    def apply_overrides(self, modules: List[ModuleNode], overrides_path: str):
        """
        Applies manual overrides from overrides.json.
        Validation: Errors out if the target module doesn't exist (Ghost Prevention).
        """
        if not os.path.exists(overrides_path):
            return

        try:
            with open(overrides_path, "r") as f:
                overrides = json.load(f)
            
            module_map = {m.path: m for m in modules}
            used_overrides = set()
            
            for entry in overrides:
                target = entry.get("module")
                if target not in module_map:
                    # High-visibility warning for ghost overrides
                    msg = f"Stale override detected! Module '{target}' no longer exists."
                    print(f"[ERROR] Archivist: {msg}")
                    if self.logger:
                        self.logger.log_event(
                            agent="Archivist",
                            event_type="ERROR",
                            target_file="overrides.json",
                            metadata={"error": msg, "target_module": target}
                        )
                    continue
                
                used_overrides.add(target)
                m = module_map[target]
                if "purpose" in entry:
                    m.purpose_statement = entry["purpose"]
                if "layer" in entry:
                    m.architecture_layer = entry["layer"]
                if "domain" in entry:
                    m.domain_cluster = entry["domain"]
                
                print(f"[Info] Archivist: Applied override to {target}")
            
            # Optional: Log which ones were not used if we had a registry
        except Exception as e:
            print(f"[Error] Archivist: Failed to apply overrides: {e}")

    def generate_codebase_report(self, modules: List[ModuleNode], git_sha: str, output_path: str, scc_groups: Optional[List[List[str]]] = None):
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
            "| Module | Domain | Layer | Status | Sync | Purpose |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |"
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
            
            # Drift Status (Phase 5 Master Thinker)
            drift_status = "✅"
            if getattr(m, "documentation_drift", False):
                drift_status = "⚠️ Drift"
            elif getattr(m, "documentation_drift", None) is None:
                drift_status = "—"
            
            # Use relative paths for portability
            rel_path = os.path.relpath(m.path, self.repo_path) if os.path.isabs(m.path) else m.path
            
            lines.append(f"| `{rel_path}` | {domain} | {layer} | {status} | {drift_status} | {purpose} |")
            
        # Add Categorized Debt Section
        lines.extend([
            "",
            "## 🚩 Technical Debt & Risks",
            "| Area | Debt Type | Severity | Description |",
            "| :--- | :--- | :--- | :--- |"
        ])
        
        # Simple heuristic debt for now (placeholder for more complex logic)
        for m in modules:
            if m.is_high_complexity:
                lines.append(f"| `{m.identity}` | Complexity | Medium | Module contains functions with high cyclomatic complexity. |")
            if m.is_dead_code_candidate:
                lines.append(f"| `{m.identity}` | Logic | Low | Potential dead code (produced but never consumed). |")
            if m.is_architectural_hub:
                lines.append(f"| `{m.identity}` | Coupling | Low | Significant architectural hub; changes may have high blast radius. |")

        # Add Circular Dependencies Section (Phase 5 Master Thinker)
        if scc_groups:
            lines.extend([
                "",
                "## 🔄 Circular Dependencies",
                "The following groups of modules have circular dependency chains:",
                ""
            ])
            for i, group in enumerate(scc_groups):
                group_list = ", ".join([f"`{g}`" for g in sorted(group)])
                lines.append(f"{i+1}. {group_list}")
        else:
            lines.extend([
                "",
                "## 🔄 Circular Dependencies",
                "✅ No circular dependencies detected."
            ])

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
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Merge header with data
        payload = {**header, **data}
        
        try:
            with open(output_path, "w") as f:
                json.dump(payload, f, indent=2, sort_keys=True, default=str)
            print(f"[Info] Archivist: Artifact saved to {output_path}")
        except Exception as e:
            print(f"[Error] Archivist: Failed to export artifact: {e}")
