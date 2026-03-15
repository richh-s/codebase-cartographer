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
    def generate_codebase_report(self, 
                                 modules: List[ModuleNode], 
                                 git_sha: str, 
                                 output_path: str, 
                                 scc_groups: Optional[List[List[str]]] = None,
                                 lineage_summary: Optional[Dict[str, Any]] = None,
                                 critical_path: Optional[List[str]] = None):
        """
        Generates a premium, deterministic CODEBASE.md summarizing the repository context.
        Includes a highlighted Critical Path, Data Flow summary, and categorized risks.
        """
        # Deterministic sort for the inventory
        modules_sorted = sorted(modules, key=lambda m: (m.domain_cluster or "General", m.path))
        
        lines = [
            "# 🗺️ Codebase Technical Overview",
            f"**Commit SHA:** `{git_sha}`",
            f"**Analysis Timestamp:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
            f"**Total Modules:** {len(modules)}",
            "",
            "## 🏗️ Architecture Layer Summary",
            "This repository is organized into functional layers that manage data flow and logic.",
            ""
        ]

        # Summary of layers
        layer_counts = {}
        for m in modules:
            layer_counts[m.architecture_layer] = layer_counts.get(m.architecture_layer, 0) + 1
        
        lines.append("| Layer | Module Count | Description |")
        lines.append("| :--- | :--- | :--- |")
        for layer, count in sorted(layer_counts.items()):
            desc = {
                "raw": "Untransformed source data.",
                "staging": "Basic cleaning and standardisation.",
                "product": "Core business logic and final models.",
                "meta": "Configuration and documentation.",
                "utility": "Shared helper functions.",
                "core": "Primary application logic."
            }.get(layer, "General system component.")
            lines.append(f"| **{layer}** | {count} | {desc} |")
        lines.append("")

        # 1. Critical Path Highlight (New Visual Style)
        lines.append("## 📈 Critical Dependency Path")
        if critical_path:
            lines.append("The sequence below represents the longest data transformation chain. "
                         "Changes to these files have the highest probability of cascading impacts:")
            lines.append("")
            # Visual breadcrumbs
            path_display = "  \n  └─ ".join([f"**{p}**" for p in critical_path])
            lines.append(f"┌─ {path_display}")
        else:
            lines.append("> *No significant multi-stage data path detected.*")
        lines.append("")

        # 2. Key Architectural Hubs (Blast Radius Risk)
        lines.append("## 🚩 High-Impact Modules (Architectural Hubs)")
        hubs = sorted([m for m in modules if m.is_architectural_hub], key=lambda x: x.pagerank_score, reverse=True)[:5]
        if hubs:
            lines.append("The following files are central to the codebase. Modifications here require careful review.")
            lines.append("| Hub Module | Importance | Layer | Potential Risk |")
            lines.append("| :--- | :--- | :--- | :--- |")
            for h in hubs:
                lines.append(f"| `{h.identity}` | **{h.importance_score}** | {h.architecture_layer} | High Blast Radius |")
        else:
            lines.append("_No major architectural hubs identified._")
        lines.append("")

        # 3. Data Sources & Sinks
        lines.append("## 🚿 Data Life Cycle")
        if lineage_summary:
            sources = lineage_summary.get("sources", [])
            sinks = lineage_summary.get("sinks", [])
            lines.append(f"- **Primary Sources:** {len(sources)} entry points detected.")
            lines.append(f"- **Primary Sinks:** {len(sinks)} terminal datasets detected.")
            
            if sources:
                lines.append("\n**Key Sources:** " + ", ".join([f"`{s['name']}`" for s in sources[:5]]))
            if sinks:
                lines.append("\n**Key Sinks:** " + ", ".join([f"`{s['name']}`" for s in sinks[:5]]))
        lines.append("")

        # 4. Detailed Module Inventory
        lines.append("## 📂 Module Inventory")
        lines.append("| Module | Layer | Importance | Purpose |")
        lines.append("| :--- | :--- | :--- | :--- |")
        
        for m in modules_sorted:
            purpose = (m.purpose_statement or "No purpose statement generated.").split('.')[0] + "." # First sentence
            lines.append(f"| `{m.path}` | {m.architecture_layer} | {m.importance_score} | {purpose} |")
            
        # 5. Domain Decomposition
        lines.append("\n## 🏷️ Business Domain Map")
        domains = {}
        for m in modules:
            domains.setdefault(m.domain_cluster or "General", []).append(m)
        
        for domain, d_modules in sorted(domains.items()):
            lines.append(f"### {domain}")
            item_lines = []
            for m in d_modules:
                item_lines.append(f"- **`{m.path}`**: {m.purpose_statement}")
            lines.extend(item_lines)
            lines.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(lines))
        
        if self.logger:
            self.logger.log_event("Archivist", "ARTIFACT_GENERATED", os.path.basename(output_path), "artifact_synthesis", 1.0)
        
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
            
            if self.logger:
                self.logger.log_event("Archivist", "ARTIFACT_GENERATED", os.path.basename(output_path), "graph_export", 1.0)
                
            print(f"[Info] Archivist: Artifact saved to {output_path}")
        except Exception as e:
            print(f"[Error] Archivist: Failed to export artifact: {e}")
