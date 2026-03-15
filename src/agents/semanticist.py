import json
from typing import List, Dict, Any, Optional
from models.nodes import ModuleNode
from utils.llm_client import LLMClient, ContextWindowBudget
from utils.module_summary import build_module_summary
from utils.similarity import cosine_similarity
from utils.clustering import cluster_into_domains

class SemanticistAgent:
    """
    Agent responsible for semantic understanding, purpose extraction,
    documentation drift detection, and domain clustering.
    """
    def __init__(self, llm_client: Optional[LLMClient] = None, logger: Optional[Any] = None):
        self.llm = llm_client or LLMClient(logger=logger)
        self.budget = self.llm.budget
        self.logger = logger

    def analyze_modules(self, target_modules: List[ModuleNode], store_embeddings: bool = False, 
                        n_clusters: Optional[int] = None, all_modules: Optional[List[ModuleNode]] = None) -> List[ModuleNode]:
        """
        Runs the full semantic analysis pipeline.
        - target_modules: Modules needing new LLM purpose extraction.
        - all_modules: Full list of modules for global clustering consistency.
        """
        # 1. Purpose Extraction (Only for targets)
        target_modules = sorted(target_modules, key=lambda m: m.identity)
        self.budget.modules_eligible = len(target_modules)
        
        batch_size = 10
        for i in range(0, len(target_modules), batch_size):
            if not self.budget.can_afford_batch(100):
                break
                
            batch = target_modules[i:i + batch_size]
            summaries = [build_module_summary(m) for m in batch]
            purposes = self.llm.get_purpose_statements(summaries)
            
            for m, p in zip(batch, purposes):
                m.purpose_statement = p.get("purpose_statement")
                m.purpose_confidence = p.get("purpose_confidence", 0.7)
                self._detect_drift(m)

        # 2. Embedding & Clustering (Over ALL modules for consistency)
        clustering_pool = all_modules if all_modules else target_modules
        eligible_for_clustering = [m for m in clustering_pool if m.purpose_statement and (m.purpose_confidence or 0) >= 0.0]
        
        # Default labels
        for m in clustering_pool:
            if m.purpose_statement and (m.purpose_confidence or 0) < 0.55:
                m.domain_cluster = "Unclassified"
            elif m.purpose_statement and len(clustering_pool) < 4:
                m.domain_cluster = "Unclustered"

        if len(eligible_for_clustering) >= 4:
            purpose_texts = [m.purpose_statement for m in eligible_for_clustering]
            embeddings = self.llm.embed_texts(purpose_texts)
            
            if store_embeddings:
                for m, emb in zip(eligible_for_clustering, embeddings):
                    m.semantic_embedding = emb
            
            labels = cluster_into_domains(embeddings, len(clustering_pool), n_clusters=n_clusters)
            for m, label in zip(eligible_for_clustering, labels):
                m.domain_cluster = f"Cluster_{label}"
            
            self.label_domain_clusters(eligible_for_clustering)
        
        return target_modules

    def _detect_drift(self, module: ModuleNode):
        """Measures semantic similarity and identifies specific contradictions."""
        summary = build_module_summary(module)
        docstring = summary.get("docstring")
        
        if docstring and module.purpose_statement:
            prompt = f"""
            Compare the following two descriptions of the software module `{module.path}`:
            
            Docstring: "{docstring}"
            Actual Purpose (derived from code): "{module.purpose_statement}"
            
            Identify if there is a 'Documentation Drift' (the docstring no longer matches the implementation).
            
            Return JSON:
            {{
              "is_drift": true|false,
              "severity": "high"|"medium"|"low"|null,
              "contradiction": "Specific explanation of the discrepancy, or null if no drift."
            }}
            """
            response = self.llm._call_with_retry("bulk", prompt, is_json=True)
            if response:
                try:
                    if "```json" in response:
                        response = response.split("```json")[1].split("```")[0].strip()
                    data = json.loads(response)
                    module.documentation_drift = data.get("is_drift", False)
                    # We can store extra metadata in the object if models allow, 
                    # for now we ensure the boolean is set and can log the contradiction.
                    module.metadata["drift_severity"] = data.get("severity")
                    module.metadata["drift_contradiction"] = data.get("contradiction")
                    
                    if self.logger:
                        self.logger.log_event(
                            "Semanticist", 
                            "SEMANTIC_ENRICHMENT", 
                            module.path, 
                            "llm_inference", 
                            1.0, 
                            metadata={
                                "feature": "drift_detection",
                                "is_drift": module.documentation_drift,
                                "severity": data.get("severity"),
                                "contradiction": data.get("contradiction")
                            }
                        )
                except Exception:
                    # Fallback to simple embedding similarity if LLM synthesis fails
                    embeddings = self.llm.embed_texts([docstring, module.purpose_statement], task_type="retrieval_document")
                    similarity = cosine_similarity(embeddings[0], embeddings[1])
                    module.documentation_drift = similarity < 0.65
        else:
            module.documentation_drift = None

    def label_domain_clusters(self, modules: List[ModuleNode]):
        """
        Refines numeric cluster labels into business domain names using LLM.
        """
        # Group modules by cluster
        clusters = {}
        for m in modules:
            if m.domain_cluster and m.domain_cluster.startswith("Cluster_"):
                clusters.setdefault(m.domain_cluster, []).append(m)
        
        for cluster_id, cluster_modules in clusters.items():
            # Prompt for domain naming
            module_data = [
                {"path": m.path, "purpose": m.purpose_statement} 
                for m in cluster_modules[:10] # Representative sample
            ]
            
            prompt = f"""
            Identify a concise BUSINESS DOMAIN name for the following group of software modules.
            Examples: "User Authentication", "Order Processing", "Data Ingestion", "Analytics Dashboard".
            
            Modules:
            {json.dumps(module_data, indent=2)}
            
            Return ONLY the domain name as a JSON string:
            {{"domain_name": "..."}}
            """
            
            response = self.llm._call_with_retry("synthesis", prompt, is_json=True)
            if response:
                try:
                    if "```json" in response:
                        response = response.split("```json")[1].split("```")[0].strip()
                    data = json.loads(response)
                    domain_name = data.get("domain_name", cluster_id)
                    for m in cluster_modules:
                        m.domain_cluster = domain_name
                except Exception:
                    pass # Keep Cluster_N name fallback

    def answer_day_one_questions(self, graph_context: Dict[str, Any], evidence_packets: List[Dict[str, Any]]) -> str:
        """
        Synthesizes high-level analysis with evidence citations.
        """
        prompt = f"""
        You are a Senior Data Engineer conducting a Phase 0 Reconnaissance of a new codebase.
        Answer the following FDE (Five Data Engineer) Questions based ONLY on the provided evidence.
        
        Questions:
        ### 1. What is the primary data ingestion path? (Identify entry points)
        ### 2. What are the 3-5 most critical output datasets/endpoints? (Identify sink nodes)
        ### 3. What is the blast radius if the most critical module fails? (Quantify downstream impact)
        ### 4. Where is the business logic concentrated vs. distributed? (Map architectural hubs)
        ### 5. What has changed most frequently in the last 90 days? (Identify high-velocity pain points)
        
        INSTRUCTIONS:
        - You MUST use the exact headers provided above.
        - Under each header, provide a technical answer based on the evidence.
        - You MUST cite specific modules and line numbers (e.g., [src/main.py:10]).
        - If evidence is missing for a question, state "Insufficient direct evidence; inferring from structural hubs...".
        
        Evidence (Modules & Purposes):
        {json.dumps(evidence_packets[:20], indent=2)}
        
        Graph Metrics:
        {json.dumps(graph_context, indent=2)}
        """
        
        response = self.llm._call_with_retry("synthesis", prompt, is_json=False)
        if not response or "Failed to synthesize answers" in response:
            # Fallback to a structured non-LLM synthesis if API fails
            fallback = "## Phase 0: System Analysis (Fallback Synthesis)\n\n"
            fallback += "### Observation Summary\n"
            fallback += f"The system analyzed {graph_context.get('module_count', 0)} modules and "
            fallback += f"identified {graph_context.get('data_node_count', 0)} primary data entities.\n\n"
            fallback += "### Data Entities\n"
            for packet in evidence_packets[:5]:
                fallback += f"- **{packet['module']}**: {packet['purpose']}\n"
            fallback += "\n### Recommendation\nManual review of `module_graph.json` is recommended as LLM synthesis was unavailable."
            return fallback

        return response
