import os
import json
import ast
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from agents.surveyor import SurveyorAgent
from agents.hydrologist import HydrologistAgent
from agents.semanticist import SemanticistAgent
from agents.archivist import ArchivistAgent
from utils.git_provider import GitProvider
from utils.trace_logger import TraceLogger, TraceEvents, Agents
from models.lineage import DatasetRole

class Orchestrator:
    """
    Wires Surveyor, Hydrologist, Semanticist, and Archivist in sequence, 
    orchestrating the full codebase analysis pipeline with Agent 4 excellence.
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)
        self.output_dir = os.path.join(self.repo_path, ".cartography")
        self.artifacts_dir = os.path.join(self.repo_path, "artifacts")
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.artifacts_dir, exist_ok=True)
        
        self.git = GitProvider(self.repo_path)
        self.logger = TraceLogger(self.output_dir)
        self.surveyor = SurveyorAgent(self.repo_path)
        self.hydrologist = HydrologistAgent(self.repo_path)
        self.semanticist = SemanticistAgent()
        self.archivist = ArchivistAgent(self.repo_path)
        
        self.cache_path = os.path.join(self.output_dir, "cache.json")
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r") as f:
                    data = json.load(f)
                if data.get("cache_schema_version") == "1.0":
                    return data
            except:
                pass
        return {"cache_schema_version": "1.0", "files": {}}

    def _save_cache(self):
        with open(self.cache_path, "w") as f:
            json.dump(self.cache, f, indent=2)

    def _compute_ast_hash(self, file_path: str) -> Optional[str]:
        """Computes a SHA256 hash of the normalized AST structure."""
        # Ensure we use the absolute path for reading
        abs_path = file_path if os.path.isabs(file_path) else os.path.join(self.repo_path, file_path)
        
        if not os.path.exists(abs_path):
            return None
        try:
            with open(abs_path, "r") as f:
                source = f.read()
            tree = ast.parse(source)
            ast_dump = ast.dump(tree, annotate_fields=False)
            return hashlib.sha256(ast_dump.encode("utf-8")).hexdigest()
        except Exception:
            try:
                with open(abs_path, "rb") as f:
                    return hashlib.sha256(f.read()).hexdigest()
            except:
                return None
        
    def run_analysis(self, llm_enabled: bool = False, semantic_depth: str = "light", 
                     store_embeddings: bool = False, velocity_days: int = 30, sql_dialect: str = "duckdb"):
        """Executes the suite with incremental intelligence and Agent 4 excellence."""
        git_sha = self.git.get_current_sha()
        self.logger.log_event(Agents.ORCHESTRATOR, TraceEvents.FILE_PARSED, "repo_root", metadata={"sha": git_sha})
        
        print(f"--- Starting Full Analysis (Git: {git_sha}) ---")
        
        # Prefetch Git Metrics
        self.git.prefetch_metadata(days=velocity_days)

        # 1. Run Surveyor for Structural Graph
        print(f"[1/3] Running Surveyor Agent...")
        start_time = datetime.now()
        module_graph_builder = self.surveyor.run()
        duration = int((datetime.now() - start_time).total_seconds() * 1000)
        self.logger.log_event(Agents.SURVEYOR, TraceEvents.ARTIFACT_GENERATED, "module_graph.json", duration_ms=duration)
        
        modules = list(module_graph_builder.nodes.values())
        
        # 2. Run Hydrologist for Data Lineage Graph
        print(f"[2/3] Running Hydrologist Agent...")
        start_time = datetime.now()
        lineage_graph = self.hydrologist.run(sql_dialect=sql_dialect)
        duration = int((datetime.now() - start_time).total_seconds() * 1000)
        self.logger.log_event(Agents.HYDROLOGIST, TraceEvents.ARTIFACT_GENERATED, "lineage_graph.json", duration_ms=duration)
        
        # 3. Handle Incremental Logic (Depth 1)
        changed_modules = []
        for m in modules:
            new_hash = self._compute_ast_hash(m.path)
            old_hash = self.cache["files"].get(m.path)
            
            if new_hash != old_hash:
                changed_modules.append(m)
                self.cache["files"][m.path] = new_hash
                
        # Flag Dep-1 neighbors for re-analysis
        if llm_enabled and changed_modules:
            blast_radius = set()
            for cm in changed_modules:
                blast_radius.add(cm.identity)
                # Find direct importers (Depth 1)
                for u, v in module_graph_builder.graph.in_edges(cm.identity):
                    blast_radius.add(u)
            
            re_analyze_targets = [m for m in modules if m.identity in blast_radius]
            print(f"[Info] Incremental: Re-analyzing {len(re_analyze_targets)} modules (Blast Radius D1)")
            self.semanticist.analyze_modules(re_analyze_targets, store_embeddings=store_embeddings)
        elif llm_enabled:
            print("[Info] Incremental: No AST changes detected. Skipping LLM re-analysis.")
        
        # 4. Archivist Enrichment
        print("[4/4] Archivist: Consolidating and Exporting Artifacts...")
        
        # Apply Overrides
        overrides_path = os.path.join(self.repo_path, "overrides.json")
        self.archivist.apply_overrides(modules, overrides_path)
        
        # Attach Git Metrics to Modules for the report
        for m in modules:
            metrics = self.git.get_file_metrics(m.path)
            m.commit_count_30d = metrics.get("commit_count_30d", 0)
            m.unique_authors_30d = metrics.get("unique_authors_30d", 0)

        # Propagate Domains & Handle Truth Hierarchy
        self._propagate_domains(modules, lineage_graph)

        # Generate Reports in artifacts/
        self.archivist.generate_codebase_report(
            modules, git_sha, os.path.join(self.artifacts_dir, "CODEBASE.md")
        )
        self.generate_reconnaissance_report(
            modules, lineage_graph, os.path.join(self.artifacts_dir, "onboarding_brief.md")
        )

        # Final Stable Exports
        m_graph_path = os.path.join(self.artifacts_dir, f"module_graph_git_{git_sha[:8]}.json")
        l_graph_path = os.path.join(self.artifacts_dir, f"lineage_graph_git_{git_sha[:8]}.json")
        
        self.archivist.export_graph_json(module_graph_builder.export_dict(), git_sha, m_graph_path)
        
        # Validate and export lineage
        lineage_graph.validate_or_raise()
        self.archivist.export_graph_json(lineage_graph.serialize_stable(), git_sha, l_graph_path)
        
        self._save_cache()
        print(f"--- Analysis Complete! Artifacts in {self.artifacts_dir} ---")
        return {
            "module_graph": m_graph_path,
            "lineage_graph": l_graph_path
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

    def generate_reconnaissance_report(self, modules: List[Any], lineage_graph: Any, output_path: str):
        """
        Compiles evidence and generates a business-level reconnaissance report.
        Standardizes on 'onboarding_brief.md' for Phase 4.
        """
        evidence_packets = []
        for m in modules:
            if m.purpose_statement:
                evidence_lines = []
                for f in m.functions[:2]:
                    evidence_lines.append({"file": m.path, "line": (f.line_range[0] if hasattr(f, "line_range") and f.line_range else 1)})
                
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
        
        with open(output_path, "w") as f:
            f.write(f"# Phase 0: Business Reconnaissance Report (Onboarding Brief)\n\n")
            f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            f.write(report_content)
        
        print(f"[Info] Archivist: Onboarding Brief saved to {output_path}")

def analyze_repo(path: str, llm_enabled: bool = False, semantic_depth: str = "light", store_embeddings: bool = False):
    """Convenience function for CLI/external calls."""
    orchestrator = Orchestrator(path)
    return orchestrator.run_analysis(llm_enabled, semantic_depth, store_embeddings)
