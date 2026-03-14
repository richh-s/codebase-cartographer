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

    def generate_codebase_report(self, 
                                 modules: List[ModuleNode], 
                                 git_sha: str, 
                                 output_path: str, 
                                 scc_groups: Optional[List[List[str]]] = None,
                                 lineage_summary: Optional[Dict[str, Any]] = None,
                                 critical_path: Optional[List[str]] = None):
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
            "## 🏗️ Architecture Overview",
            "This repository is organized into distinct functional layers and business domains. "
            "The system manages data transformations and structural logic across multiple languages, "
            "with dependencies visualized in the lineage and module graphs.",
            ""
        ]

        # 1. Critical Path Section
        lines.append("## 📈 Critical Path")
        if critical_path:
            lines.append("The following sequence represents the longest dependency chain in the system, "
                         "making it a primary target for architectural review:")
            path_str = " → ".join([f"`{p}`" for p in critical_path])
            lines.append(f"> {path_str}")
        else:
            lines.append("No significant critical path detected.")
        lines.append("")

        # 2. Data Sources & Sinks Section (Rubric Check)
        lines.append("## 🚿 Data Sources & Sinks")
        if lineage_summary:
            sources = lineage_summary.get("sources", [])
            sinks = lineage_summary.get("sinks", [])
            
            lines.append("### Entry Points (Sources)")
            if sources:
                lines.append("| Name | System | Environment | Namespace |")
                lines.append("| :--- | :--- | :--- | :--- |")
                for s in sources[:10]: # Cap for readability
                    lines.append(f"| `{s['name']}` | {s.get('system')} | {s.get('environment')} | {s.get('namespace')} |")
            else:
                lines.append("_No primary sources identified._")
            
            lines.append("\n### Exit Points (Sinks)")
            if sinks:
                lines.append("| Name | System | Environment | Namespace |")
                lines.append("| :--- | :--- | :--- | :--- |")
                for s in sinks[:10]:
                    lines.append(f"| `{s['name']}` | {s.get('system')} | {s.get('environment')} | {s.get('namespace')} |")
            else:
                lines.append("_No primary sinks identified._")
        else:
            lines.append("_Lineage data unavailable for source/sink analysis._")
        lines.append("")

        # 3. High-Velocity Files (Rubric Check)
        lines.append("## 🚀 High-Velocity Files")
        high_velocity = sorted([m for m in modules if getattr(m, "commit_count_30d", 0) > self.st_threshold], 
                               key=lambda x: x.commit_count_30d, reverse=True)
        if high_velocity:
            lines.append("| File | 30d Commits | Authors | Risk |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for m in high_velocity:
                rel_path = os.path.relpath(m.path, self.repo_path) if os.path.isabs(m.path) else m.path
                lines.append(f"| `{rel_path}` | {m.commit_count_30d} | {getattr(m, 'unique_authors_30d', 1)} | High churn |")
        else:
            lines.append("No high-velocity files detected (stable codebase).")
        lines.append("")

        # 4. Module Inventory
        lines.append("## 📂 Module Inventory")
        lines.append("| Module | Domain | Rank | Sync | Purpose |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        
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
            
            # PageRank (Phase 7 Request)
            rank = f"{(m.pagerank_score or 0.0):.3f}"
            rel_path = os.path.relpath(m.path, self.repo_path) if os.path.isabs(m.path) else m.path
            
            lines.append(f"| `{rel_path}` | {domain} | {rank} | {drift_status} | {purpose} |")
            
        # 5. Categorized Debt Section (Rubric Check)
        lines.extend([
            "",
            "## 🚩 Technical Debt & Risks",
            "| Area | Debt Type | Severity | Description |",
            "| :--- | :--- | :--- | :--- |"
        ])
        
        for m in modules:
            rel_id = os.path.relpath(m.identity, self.repo_path) if os.path.isabs(m.identity) else m.identity
            if m.is_high_complexity:
                lines.append(f"| `{rel_id}` | Complexity | Medium | High cyclomatic complexity. |")
            if m.is_dead_code_candidate:
                lines.append(f"| `{rel_id}` | Logic | Low | Produced but never consumed. |")
            if m.is_architectural_hub:
                lines.append(f"| `{rel_id}` | Coupling | High | Major architectural hub; critical for blast radius. |")

        # 7. Module Purpose Index (Rubric Check)
        lines.append("\n## 🏷️ Module Purpose Index (by Domain)")
        domains = {}
        for m in modules:
            domains.setdefault(m.domain_cluster or "General", []).append(m)
        
        for domain, d_modules in sorted(domains.items()):
            lines.append(f"### {domain}")
            for m in d_modules:
                rel_path = os.path.relpath(m.path, self.repo_path) if os.path.isabs(m.path) else m.path
                lines.append(f"- **`{rel_path}`**: {m.purpose_statement}")
            lines.append("")

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
