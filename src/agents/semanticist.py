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
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()
        self.budget = self.llm.budget

    def analyze_modules(self, modules: List[ModuleNode], store_embeddings: bool = False) -> List[ModuleNode]:
        """
        Runs the full semantic analysis pipeline for a list of modules.
        """
        # Sort modules by path for determinism
        modules = sorted(modules, key=lambda m: m.identity)
        self.budget.modules_eligible = len(modules)
        
        # 1. Purpose Extraction (Batched)
        batch_size = 10
        for i in range(0, len(modules), batch_size):
            # Pre-batch budget check
            if not self.budget.can_afford_batch(100): # Small constant for check
                break
                
            batch = modules[i:i + batch_size]
            summaries = [build_module_summary(m) for m in batch]
            
            purposes = self.llm.get_purpose_statements(summaries)
            
            for m, p in zip(batch, purposes):
                m.purpose_statement = p.get("purpose_statement")
                m.purpose_confidence = p.get("purpose_confidence")
                
                # Detect Drift (if docstring and purpose exist)
                self._detect_drift(m)

        # 2. Embedding & Clustering
        # Only cluster modules with purpose_confidence >= 0.55
        eligible_for_clustering = [m for m in modules if m.purpose_statement and (m.purpose_confidence or 0) >= 0.55]
        
        # Default all to Unclassified if they have a purpose but low confidence
        for m in modules:
            if m.purpose_statement and (m.purpose_confidence or 0) < 0.55:
                m.domain_cluster = "Unclassified"
            elif m.purpose_statement and len(modules) < 4:
                m.domain_cluster = "Unclustered"

        if len(eligible_for_clustering) >= 4:
            purpose_texts = [m.purpose_statement for m in eligible_for_clustering]
            embeddings = self.llm.embed_texts(purpose_texts)
            
            # Store embeddings if flag enabled
            if store_embeddings:
                for m, emb in zip(eligible_for_clustering, embeddings):
                    m.semantic_embedding = emb
            
            # Perform Clustering
            labels = cluster_into_domains(embeddings, len(modules))
            
            for m, label in zip(eligible_for_clustering, labels):
                # Placeholder for label_domain_clusters logic
                m.domain_cluster = f"Cluster_{label}"
            
            # Label Clusters with LLM
            self.label_domain_clusters(eligible_for_clustering)
        
        return modules

    def _detect_drift(self, module: ModuleNode):
        """Measures semantic similarity between docstring and LLM purpose."""
        # Get module docstring (from summary logic or AST)
        summary = build_module_summary(module)
        docstring = summary.get("docstring")
        
        if docstring and module.purpose_statement:
            # We need embeddings for drift detection
            embeddings = self.llm.embed_texts([docstring, module.purpose_statement], task_type="retrieval_document")
            similarity = cosine_similarity(embeddings[0], embeddings[1])
            
            # Threshold < 0.65 marks drift
            module.documentation_drift = similarity < 0.65
        else:
            module.documentation_drift = None # Unknown

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
            
            response = self.llm._call_with_retry("gemini-1.5-flash", prompt, is_json=True)
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
        1. What business capability does this system provide?
        2. Where is the 'Source of Truth' and which systems are the sinks?
        3. What are the key data transformation layers?
        4. What is the overall architectural health (debt, complexity)?
        5. What is the 'Blast Radius' of a change to core schemas?
        
        CRITICAL: Every claim MUST have a citation in [file_path:line_number] format.
        
        Evidence:
        {json.dumps(evidence_packets, indent=2)}
        
        Graph Context (Summary of counts and nodes):
        {json.dumps(graph_context, indent=2)}
        """
        
        response = self.llm._call_with_retry("gemini-1.5-flash", prompt, is_json=False)
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
