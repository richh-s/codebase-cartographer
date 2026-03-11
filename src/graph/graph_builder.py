import json
import os
import networkx as nx
from typing import Dict, List, Any

from models.nodes import ModuleNode

class GraphBuilder:
    """Constructs and analyzes the codebase dependency graph using a NetworkX DiGraph."""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, ModuleNode] = {}
        
    def add_module(self, node: ModuleNode):
        self.nodes[node.identity] = node
        self.graph.add_node(node.identity, **node.model_dump())
        
    def build_edges(self):
        """Creates edges based on imports and extracted references."""
        # Create lookups to map import strings to node identities
        lookup = {}
        for nid, n in self.nodes.items():
            base_name, ext = os.path.splitext(os.path.basename(n.path))
            # dbt ref() matches the file's base name exactly (e.g. 'stg_orders')
            lookup[base_name] = nid  
            
            # For Python: Try to match dot-notated module imports (e.g. 'utils.git_utils')
            if ext == '.py':
                path_without_ext = n.path[:-3]
                parts = path_without_ext.split('/')
                for i in range(len(parts)):
                    lookup[".".join(parts[i:])] = nid
            
        for identity, node in self.nodes.items():
            for imported_obj in node.imports:
                imported_name = imported_obj.get("name", "")
                edge_type = imported_obj.get("type", "unknown")
                
                target_id = lookup.get(imported_name)
                if not target_id:
                    # Fallback for dbt source('schema', 'table') -> 'schema.table'
                    if '.' in imported_name:
                        target_id = lookup.get(imported_name.split('.')[-1])
                        
                if target_id and target_id != identity:
                    # Typocast schema/metadata edges properly
                    if identity.endswith('.yml') or identity.endswith('.yaml') or target_id.endswith('.yml') or target_id.endswith('.yaml'):
                        edge_type = "describes"
                    # Typocast seeds explicitly to source rather than ref for lineage clarity
                    elif target_id.startswith('seeds/') or target_id.startswith('data/'):
                        edge_type = "dbt_source"
                        
                    # Direction: Dependency -> Dependent (e.g., stg_orders -> orders)
                    # This allows PageRank to flow toward the most referenced models.
                    self.graph.add_edge(target_id, identity, type=edge_type)

    def _resolve_import(self, import_str: str) -> str:
        # Placeholder for more complex import resolution logic if needed
        return import_str

    def compute_intelligence(self, pagerank_threshold: float = 0.15):
        """Calculates PageRank, SCCs, and flags Dead Code / Sink Nodes."""
        if not self.graph.nodes:
            return

        N = len(self.graph.nodes)
        
        # 1. PageRank (Architectural Hubs)
        try:
            # Prevent informational/doc files from absorbing PageRank
            executable_nodes = [
                nid for nid in self.graph.nodes
                if not self.nodes[nid].is_informational
            ]
            eval_graph = self.graph.subgraph(executable_nodes)
            
            sub_pagerank = nx.pagerank(eval_graph)
            
            # Re-map scores to full graph (info nodes get 0.0 natively)
            pagerank = {n: 0.0 for n in self.graph.nodes}
            pagerank.update(sub_pagerank)
        except Exception:
            pagerank = {n: 0.0 for n in self.graph.nodes}
            
        # 2. SCCs (Circular Dependencies)
        scc_gen = nx.strongly_connected_components(self.graph)
        self.scc_groups = [list(c) for c in scc_gen if len(c) > 1]
        
        # 3. Apply metrics and classify nodes
        # Baseline threshold scales with 1/N. Anything significantly above 1/N is acting as a hub or sink.
        pr_baseline = 1.0 / N if N > 0 else 0.0
        # Increased multiplier from 1.5 to 2.5 to be more restrictive of what gets called a 'hub'
        pr_threshold = max(pagerank_threshold, pr_baseline * 2.5)
        
        # Calculate min/max PageRank for normalization
        pr_values = [v for v in pagerank.values() if v > 0]
        min_pr = min(pr_values) if pr_values else 0.0
        max_pr = max(pr_values) if pr_values else 1.0
        if max_pr == min_pr:
            max_pr = min_pr + 1e-9 # Prevent division by zero
            
        for identity, data in self.graph.nodes(data=True):
            node = self.nodes[identity]
            pr_score = pagerank.get(identity, 0.0)
            
            node.pagerank_score = pr_score
            
            # Normalize to 1-100 Importance Score
            if pr_score > 0:
                normalized = 1 + int(((pr_score - min_pr) / (max_pr - min_pr)) * 99)
                node.importance_score = max(1, min(100, normalized))
            else:
                node.importance_score = 1
                
            # Baseline importance for data sources (seeds/raw)
            if node.architecture_layer == "raw" or "seeds/" in node.path or "data/" in node.path:
                node.importance_score = max(node.importance_score, 20)
            
            # Use strict informational flag isolation
            if pr_score > pr_threshold and not node.is_informational:
                 node.is_architectural_hub = True
            
            in_degree = self.graph.in_degree(identity)
            out_degree = self.graph.out_degree(identity)
            
            # Identify Sink Nodes
            is_in_output_dir = "models/" in node.path or "marts/" in node.path
            if out_degree == 0 and (pr_score > pr_threshold or is_in_output_dir) and not node.is_informational:
                node.is_sink_node = True
                
            # Identify Dead Code Candidates
            # Explicitly force informational components to skip dead code analysis entirely
            if node.is_informational:
                node.is_dead_code_candidate = False
            else:
                is_seed_or_data = node.path.startswith("seeds/") or node.path.startswith("data/")
                if out_degree == 0 and not is_seed_or_data and not node.is_sink_node:
                    # It's not imported by anyone (no outgoing data flow), not a seed, and not an explicit sink
                    node.is_dead_code_candidate = True
                
            # Update the graph data dict to reflect changes made to the Pydantic model
            self.graph.nodes[identity].update(node.model_dump())

    def export_json(self, output_path: str):
        """Serializes the graph to the required JSON schema."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Top hubs: sort by pagerank descending (only include those that pass the threshold)
        hub_candidates = [n for n in self.nodes.values() if n.is_architectural_hub]
        sorted_nodes = sorted(
            hub_candidates, 
            key=lambda n: n.pagerank_score, 
            reverse=True
        )
        top_hubs = [n.identity for n in sorted_nodes[:10]]
        
        # Format structured JSON edges with sorting
        structured_edges = sorted([
            {"source": u, "target": v, "type": d.get("type", "unknown")}
            for u, v, d in self.graph.edges(data=True)
        ], key=lambda x: (x["source"], x["target"]))
        
        # Format nodes sorted by identity
        sorted_nodes_list = sorted(
            [n.model_dump() for n in self.nodes.values()],
            key=lambda x: x["identity"]
        )
        
        output = {
            "nodes": sorted_nodes_list,
            "edges": structured_edges,
            "top_hubs": top_hubs,
            "scc_groups": sorted([sorted(g) for g in self.scc_groups]),
            "metadata": {
                "total_files": len(self.nodes)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, sort_keys=True)
