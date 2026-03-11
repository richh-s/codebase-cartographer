import os
import json
from datetime import datetime
from agents.surveyor import SurveyorAgent
from agents.hydrologist import HydrologistAgent
from agents.semanticist import SemanticistAgent
from agents.archivist import ArchivistAgent
from models.lineage import DatasetRole

class Orchestrator:
    """
    Wires Surveyor, Hydrologist, Semanticist, and Archivist in sequence, 
    orchestrating the full codebase analysis pipeline.
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)
        self.output_dir = os.path.join(self.repo_path, ".cartography")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.surveyor = SurveyorAgent(self.repo_path)
        self.hydrologist = HydrologistAgent(self.repo_path)
        self.semanticist = SemanticistAgent()
        self.archivist = ArchivistAgent()
        
    def run_analysis(self, llm_enabled: bool = False, semantic_depth: str = "light", 
                     store_embeddings: bool = False, velocity_days: int = 30, sql_dialect: str = "duckdb"):
        """Executes the full analysis suite with rubric-compliant configuration."""
        print(f"--- Starting Full Analysis on {self.repo_path} ---")
        
        # 1. Run Surveyor for Structural Graph (Configurable velocity window)
        print(f"[1/3] Running Surveyor Agent (Velocity Window: {velocity_days} days)...")
        module_graph_builder = self.surveyor.run(
            output_json=".cartography/module_graph.json", 
            velocity_days=velocity_days
        )
        
        # 2. Run Hydrologist for Data Lineage Graph (Configurable SQL dialect)
        print(f"[2/3] Running Hydrologist Agent (SQL Dialect: {sql_dialect})...")
        lineage_graph = self.hydrologist.run(
            output_json=".cartography/lineage_graph.json",
            sql_dialect=sql_dialect
        )
        
        # 3. Run Semanticist Agent (if enabled)
        if llm_enabled:
            print("[3/3] Running Semanticist Agent...")
            modules = list(module_graph_builder.nodes.values())
            self.semanticist.analyze_modules(modules, store_embeddings=store_embeddings)
            
            # 4. Generate CODEBASE.md and RECONNAISSANCE.md
            print("[4/4] Generating Documentation Artifacts...")
            self.archivist.generate_codebase_report(modules, os.path.join(self.repo_path, "CODEBASE.md"))
            
            # Propagate Domains to DataNodes
            self._propagate_domains(modules, lineage_graph)
            
            # Re-export with semantic data
            module_graph_builder.export_json(os.path.join(self.output_dir, "module_graph.json"))
            self._re_export_lineage(lineage_graph, os.path.join(self.output_dir, "lineage_graph.json"))
            
            # Update Metadata with Semantic Metrics
            self._update_graph_metadata(llm_enabled=True)
            
            # 4. Generate Reconnaissance Report
            print("[4/4] Generating RECONNAISSANCE.md...")
            self.generate_reconnaissance_report(modules, lineage_graph)
        else:
            print("[3/3] Semantic Analysis Skipped.")
            self._update_graph_metadata(llm_enabled=False)
            
        print(f"--- Analysis Complete! Artifacts saved to {self.output_dir} ---")
        return {
            "module_graph": os.path.join(self.output_dir, "module_graph.json"),
            "lineage_graph": os.path.join(self.output_dir, "lineage_graph.json")
        }

    def _propagate_domains(self, modules: List[Any], lineage_graph: Any):
        """
        Propagates domain clusters from modules to DataNodes via transformation edges.
        """
        module_map = {m.identity: m for m in modules}
        
        for dataset_id, node in lineage_graph.data_nodes.items():
            # Find producers (Lineage: Code/Trans -> Data)
            producers = list(lineage_graph.graph.predecessors(dataset_id))
            producer_domains = []
            producer_purposes = []
            
            for p_id in producers:
                if p_id in module_map:
                    m = module_map[p_id]
                    if m.domain_cluster:
                        producer_domains.append(m.domain_cluster)
                    if m.purpose_statement:
                        producer_purposes.append(m.purpose_statement)
            
            if len(producer_domains) == 1:
                node.domain_cluster = producer_domains[0]
                node.purpose_statement = producer_purposes[0] if producer_purposes else None
            elif len(producer_domains) > 1:
                # Majority domain
                from collections import Counter
                counts = Counter(producer_domains)
                node.domain_cluster = counts.most_common(1)[0][0]
                # Combined purpose or representative one
                node.purpose_statement = producer_purposes[0]
            else:
                node.domain_cluster = "Unknown"

    def _re_export_lineage(self, lineage_graph: Any, out_path: str):
        """Helper to re-serialize lineage graph after semantic enrichment."""
        data_nodes = sorted(
            [n.model_dump() for n in lineage_graph.data_nodes.values()],
            key=lambda x: x["canonical_name"]
        )
        
        transformation_nodes = sorted(
            [n.model_dump() for n in lineage_graph.transformation_nodes.values()],
            key=lambda x: x["identity"]
        )
        
        edges = sorted(
            [lineage_graph.graph.edges[u, v] for u, v in lineage_graph.graph.edges()],
            key=lambda x: (x.get("source", ""), x.get("target", ""))
        )

        with open(out_path, "w") as f:
            data = {
                "version": lineage_graph.graph_version if hasattr(lineage_graph, "graph_version") else "1.0",
                "timestamp": datetime.now().isoformat(),
                "nodes": {
                    "data": data_nodes,
                    "transformations": transformation_nodes
                },
                "edges": edges,
                "health": lineage_graph.get_health_report(),
                "mermaid": lineage_graph.to_mermaid()
            }
            json.dump(data, f, indent=2, sort_keys=True, default=str)

    def _update_graph_metadata(self, llm_enabled: bool):
        """Enriches the graph metadata with semantic processing metrics."""
        paths = [
            os.path.join(self.output_dir, "module_graph.json"),
            os.path.join(self.output_dir, "lineage_graph.json")
        ]
        
        for path in paths:
            if not os.path.exists(path):
                continue
                
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                
                # Add semantic metadata
                data["semantic_analysis_complete"] = llm_enabled and (self.semanticist.budget.modules_processed >= self.semanticist.budget.modules_eligible) if llm_enabled else False
                data["semantic_modules_total"] = self.semanticist.budget.modules_eligible if llm_enabled else 0
                data["semantic_modules_processed"] = self.semanticist.budget.modules_processed if llm_enabled else 0
                
                with open(path, "w") as f:
                    json.dump(data, f, indent=2, sort_keys=True, default=str)
            except Exception as e:
                print(f"Warning: Failed to update metadata for {path}: {e}")

    def generate_reconnaissance_report(self, modules: List[Any], lineage_graph: Any):
        """
        Compiles evidence and generates a business-level reconnaissance report.
        """
        evidence_packets = []
        for m in modules:
            if m.purpose_statement:
                evidence_lines = []
                # Cite functions for code modules
                for f in m.functions[:2]:
                    evidence_lines.append({"file": m.path, "line": (f.line_range[0] if hasattr(f, "line_range") and f.line_range else 1)})
                
                # Cite file directly for non-code or simple modules
                if not evidence_lines:
                    evidence_lines.append({"file": m.path, "line": 1})
                
                packet = {
                    "module": m.identity,
                    "purpose": m.purpose_statement,
                    "evidence": evidence_lines
                }
                evidence_packets.append(packet)

        graph_context = {
            "module_count": len(modules),
            "data_node_count": len(lineage_graph.data_nodes),
            "transformation_count": len(lineage_graph.transformation_nodes),
            "edge_count": lineage_graph.graph.number_of_edges()
        }

        report_content = self.semanticist.answer_day_one_questions(graph_context, evidence_packets)
        
        report_path = os.path.join(self.repo_path, "RECONNAISSANCE.md")
        with open(report_path, "w") as f:
            f.write(f"# Phase 0: Business Reconnaissance Report\n\n")
            f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write(report_content)
        
        print(f"Report saved to {report_path}")

def analyze_repo(path: str, llm_enabled: bool = False, semantic_depth: str = "light", store_embeddings: bool = False):
    """Convenience function for CLI/external calls."""
    orchestrator = Orchestrator(path)
    return orchestrator.run_analysis(llm_enabled, semantic_depth, store_embeddings)
