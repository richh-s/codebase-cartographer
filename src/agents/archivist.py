import os
from typing import List
from models.nodes import ModuleNode

class ArchivistAgent:
    """Agent responsible for generating human-readable documentation artifacts."""
    
    def generate_codebase_report(self, modules: List[ModuleNode], output_path: str):
        """Generates a high-level CODEBASE.md overview of the repository."""
        # Sort by domain or path
        modules = sorted(modules, key=lambda m: (m.domain_cluster or "Unknown", m.path))
        
        lines = [
            "# Codebase Technical Overview",
            f"**Total Modules:** {len(modules)}",
            "",
            "## 📂 Module Inventory",
            ""
        ]
        
        current_domain = None
        for m in modules:
            domain = m.domain_cluster or "Unknown"
            if domain != current_domain:
                lines.append(f"### 🌐 Domain: {domain}")
                current_domain = domain
            
            purpose = m.purpose_statement or "No purpose statement generated."
            lines.append(f"- **{m.path}**")
            lines.append(f"  - *Layer:* {m.architecture_layer}")
            lines.append(f"  - *Purpose:* {purpose}")
            if m.importance_score:
                lines.append(f"  - *Importance:* {m.importance_score:.2f}")
            lines.append("")
            
        with open(output_path, "w") as f:
            f.write("\n".join(lines))
        print(f"Codebase report saved to {output_path}")
