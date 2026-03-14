import networkx as nx
import math
from typing import List, Dict, Any, Optional, Set
from models.lineage import DataNode, LineageEdge, TransformationNode, DatasetRole

class DataLineageGraph:
    """Manages the directed graph of data entities and their code lineages with phase 2.6 topological intelligence."""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        # Storage for rich node objects
        self.data_nodes: Dict[str, DataNode] = {}
        self.transformation_nodes: Dict[str, TransformationNode] = {}
        # We still track module identities to allow code-to-data edges
        self.module_nodes: Dict[str, Any] = {}

    def add_data_node(self, node: DataNode):
        self.data_nodes[node.identity] = node
        self.graph.add_node(node.identity, type="data", node_obj=node)

    def add_transformation_node(self, node: TransformationNode):
        self.transformation_nodes[node.identity] = node
        self.graph.add_node(node.identity, type="transformation", node_obj=node)

    def add_module_node(self, module_id: str, importance: int = 1):
        """Phase 1 legacy support."""
        self.module_nodes[module_id] = {"importance": importance}
        self.graph.add_node(module_id, type="module")

    def add_lineage_edge(self, edge: LineageEdge):
        # Create virtual nodes if they don't exist
        if edge.source not in self.graph:
            self.graph.add_node(edge.source, type="unknown")
        if edge.target not in self.graph:
            self.graph.add_node(edge.target, type="unknown")
            
        self.graph.add_edge(edge.source, edge.target, **edge.model_dump())

    def blast_radius(self, node_identity: str) -> List[str]:
        """Returns all downstream dependents of a given node identity using BFS."""
        if node_identity not in self.graph:
            return []
            
        dependents = set()
        # Use BFS to find all reachable nodes in the directed graph
        for descendant in nx.descendants(self.graph, node_identity):
            dependents.add(descendant)
            
        return sorted(list(dependents))

    def assign_roles(self):
        """Assigns semantic roles (SOURCE, INTERMEDIATE, TERMINAL) based on graph topology."""
        for node_id in self.data_nodes:
            # Phase 2.10 Fix: A node is SOURCE ONLY if it has no incoming edges at all.
            # If it has an incoming edge from a TransformationNode, it's NOT a source.
            in_edges = list(self.graph.in_edges(node_id, data=True))
            out_edges = list(self.graph.out_edges(node_id, data=True))
            
            has_transformation_input = any(
                u in self.transformation_nodes for u, v, d in in_edges
            )
            
            node = self.data_nodes[node_id]
            
            # Topological priority
            if not has_transformation_input and len(in_edges) == 0:
                node.role = DatasetRole.SOURCE
            elif len(out_edges) == 0 and len(in_edges) > 0:
                node.role = DatasetRole.TERMINAL
            else:
                node.role = DatasetRole.INTERMEDIATE
            
            # Prefix heuristics as fallback/refinement, but NEVER override topological reality
            # that would break validation.
            lname = node.name.lower()
            if node.role == DatasetRole.SOURCE:
                # If we think it's a source, confirm with prefixes
                pass 
            elif node.role == DatasetRole.INTERMEDIATE:
                if "stg_" in lname or "staging_" in lname:
                    node.role = DatasetRole.INTERMEDIATE
            
            # Safety Check: If it has incoming edges, it CANNOT be a SOURCE
            if len(in_edges) > 0 and node.role == DatasetRole.SOURCE:
                node.role = DatasetRole.INTERMEDIATE
            # Safety Check: If it has outgoing edges, it CANNOT be a TERMINAL
            if len(out_edges) > 0 and node.role == DatasetRole.TERMINAL:
                node.role = DatasetRole.INTERMEDIATE

    def compute_importance(self, structural_importances: Dict[str, int]):
        """
        Calculates a distance-weighted impact score for each DataNode.
        Formula: structural_weight + sum(1.0 / (1.5 ^ path_distance)) for all downstream nodes.
        """
        for node_id, node in self.data_nodes.items():
            base_importance = structural_importances.get(node_id, 1)
            
            # Phase 2.7: Distance-weighted impact
            impact_sum = 0.0
            try:
                paths = nx.single_source_shortest_path_length(self.graph, node_id)
                for target_id, distance in paths.items():
                    if target_id != node_id and target_id in self.data_nodes:
                        impact_sum += (1.0 / math.pow(1.5, distance))
            except nx.NetworkXError:
                pass
            
            merged = base_importance + impact_sum
            node.importance_score = min(100, int(merged * 10))  # Scale for visibility

    def validate_or_raise(self):
        """
        Validates the graph for structural integrity.
        Fills Phase 4 requirements for orphan node prevention.
        """
        warnings = self.validate_integrity()
        high_severity = [w for w in warnings if w["severity"] == "high"]
        if high_severity:
            raise ValueError(f"Graph integrity failure (High Severity): {high_severity}")

    def serialize_stable(self) -> Dict[str, Any]:
        """
        Returns a dictionary representation with sorted nodes and edges.
        Fills Phase 4 requirements for deterministic binary-identical artifacts.
        """
        # Sort data nodes by identity
        data_nodes = sorted(
            [n.model_dump() for n in self.data_nodes.values()],
            key=lambda x: x["identity"]
        )
        # Sort transformation nodes by identity
        transformation_nodes = sorted(
            [n.model_dump() for n in self.transformation_nodes.values()],
            key=lambda x: x["identity"]
        )
        # Sort edges by source then target
        edges = sorted(
            [
                {"source": u, "target": v, **d} 
                for u, v, d in self.graph.edges(data=True)
            ],
            key=lambda x: (x["source"], x["target"])
        )

        return {
            "data_nodes": data_nodes,
            "transformation_nodes": transformation_nodes,
            "edges": edges,
            "health": self.get_health_report()
        }

    def save_json(self, path: str):
        """Serializes the graph to a JSON file with stable ordering."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = self.serialize_stable()
        # sort_keys=True ensures key-level determinism
        with open(path, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True, default=str)

    def load_json(self, path: str):
        """Deserializes the graph from a JSON file."""
        with open(path, "r") as f:
            data = json.load(f)
        
        self.graph.clear()
        self.data_nodes.clear()
        self.transformation_nodes.clear()
        
        for dn in data.get("data_nodes", []):
            node = DataNode(**dn)
            self.add_data_node(node)
            
        for tn in data.get("transformation_nodes", []):
            node = TransformationNode(**tn)
            self.add_transformation_node(node)
            
        for edge in data.get("edges", []):
            source = edge.pop("source")
            target = edge.pop("target")
            self.graph.add_edge(source, target, **edge)

    def get_unified_lineage(self, node_identity: str) -> Dict[str, Any]:
        """
        Public Query API: Returns a unified summary of SQL, Python, and Config lineages for a node.
        """
        if node_identity not in self.graph:
            return {"error": "Node not found"}
            
        in_edges = []
        for u, v, d in self.graph.in_edges(node_identity, data=True):
            in_edges.append({
                "source": u,
                "type": d.get("type"),
                "origin": d.get("origin_analyzer", "unknown"),
                "confidence": d.get("confidence_score", 1.0)
            })
            
        out_edges = []
        for u, v, d in self.graph.out_edges(node_identity, data=True):
            out_edges.append({
                "target": v,
                "type": d.get("type"),
                "origin": d.get("origin_analyzer", "unknown"),
                "confidence": d.get("confidence_score", 1.0)
            })
            
        return {
            "identity": node_identity,
            "upstream": in_edges,
            "downstream": out_edges,
            "is_source": self.graph.in_degree(node_identity) == 0,
            "is_sink": self.graph.out_degree(node_identity) == 0
        }

    def find_sources(self) -> List[DataNode]:
        """Public Query API: Returns all entry points (SOURCE nodes) in the data system."""
        return [n for n in self.data_nodes.values() if n.role == DatasetRole.SOURCE]

    def find_sinks(self) -> List[DataNode]:
        """Public Query API: Returns all exit points (TERMINAL nodes) in the data system."""
        return [n for n in self.data_nodes.values() if n.role == DatasetRole.TERMINAL]

    def validate_integrity(self, canonical_registry: Optional[Dict[str, Set[tuple]]] = None) -> List[Dict[str, Any]]:
        """Phase 2.6 expanded validation."""
        warnings = []
        
        # 1. Cycle detection
        cycles = list(nx.simple_cycles(self.graph))
        if cycles:
            warnings.append({"type": "cycle", "message": f"Cycles detected: {cycles}", "severity": "high"})
            
        # 2. Unknown nodes
        for node_id in self.graph.nodes():
            if self.graph.nodes[node_id].get("type") == "unknown":
                warnings.append({"type": "undefined_reference", "message": f"Edge references undefined node: {node_id}", "severity": "medium"})
                
        # 3. Orphan data nodes
        for node_id, node in self.data_nodes.items():
            if self.graph.degree(node_id) == 0:
                warnings.append({"type": "orphan", "message": f"Data node '{node_id}' has no lineages", "severity": "low"})

        # 4. Dangling Sinks
        for node_id, node in self.data_nodes.items():
            if node.role == DatasetRole.INTERMEDIATE and self.graph.out_degree(node_id) == 0:
                warnings.append({
                    "type": "dangling_sink", 
                    "message": f"Intermediate node '{node_id}' is produced but never consumed",
                    "severity": "medium"
                })

        # 4.5. Isolated Transformations
        for node_id, node in self.transformation_nodes.items():
            if self.graph.degree(node_id) == 0:
                warnings.append({
                    "type": "isolated_transformation",
                    "message": f"Transformation '{node_id}' is disconnected from all datasets",
                    "severity": "medium"
                })

        # 5. Impossible Directions (Phase 2.6)
        for u, v, data in self.graph.edges(data=True):
            if u in self.data_nodes and v in self.transformation_nodes:
                # READ flow: Data -> Trans
                u_node = self.data_nodes[u]
                if u_node.role == DatasetRole.TERMINAL:
                    warnings.append({"type": "logic_error", "message": f"Terminal node '{u}' has outgoing read edge (impossible)", "severity": "high"})
            if u in self.transformation_nodes and v in self.data_nodes:
                # WRITE flow: Trans -> Data
                v_node = self.data_nodes[v]
                if v_node.role == DatasetRole.SOURCE:
                    warnings.append({"type": "logic_error", "message": f"Source node '{v}' has incoming write edge (impossible)", "severity": "high"})

        # 6. Suspicious Collisions
        if canonical_registry:
            for canon, occurrences in canonical_registry.items():
                if len(occurrences) > 1:
                    namespaces = list(set([o[0] for o in occurrences]))
                    if len(namespaces) > 1:
                        warnings.append({
                            "type": "collision_risk",
                            "message": f"Canonical name '{canon}' exists in multiple namespaces: {namespaces}",
                            "severity": "medium",
                            "provenance": occurrences
                        })
                
        return warnings

    def get_health_report(self) -> Dict[str, Any]:
        """Calculates graph health metrics (Phase 2.6)."""
        total_data = len(self.data_nodes)
        if total_data == 0: return {"score": 0}
        
        warnings = self.validate_integrity()
        heuristic_edges = len([d for _, _, d in self.graph.edges(data=True) if d.get('confidence_score', 1.0) < 0.5])
        total_edges = self.graph.number_of_edges()
        
        # Simple health score: 100 - (penalty per warning/heuristic)
        score = 100
        score -= len([w for w in warnings if w['severity'] == 'high']) * 20
        score -= len([w for w in warnings if w['severity'] == 'medium']) * 10
        score -= len([w for w in warnings if w['severity'] == 'low']) * 5
        
        heuristic_penalty = (heuristic_edges / total_edges * 30) if total_edges > 0 else 0
        score -= heuristic_penalty
        
        return {
            "health_score": max(0, int(score)),
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": total_edges,
            "data_nodes": total_data,
            "transformation_nodes": len(self.transformation_nodes),
            "heuristic_edges": heuristic_edges,
            "orphan_nodes": len([w for w in warnings if w['type'] == 'orphan']),
            "dangling_sinks": len([w for w in warnings if w['type'] == 'dangling_sink']),
            "isolated_transformations": len([w for w in warnings if w['type'] == 'isolated_transformation']),
            "unresolved_datasets": len([w for w in warnings if w['type'] == 'undefined_reference']),
            "warning_count": len(warnings)
        }

    def to_mermaid(self) -> str:
        """Generates a grouped Mermaid JS flowchart representation (Phase 2.8)."""
        lines = ["flowchart TD"]
        lines.append("    classDef source fill:#dfd,stroke:#383,stroke-width:2px;")
        lines.append("    classDef terminal fill:#fdd,stroke:#833,stroke-width:2px;")
        lines.append("    classDef intermediate fill:#ddf,stroke:#338;")
        lines.append("    classDef trans fill:#f9f,stroke:#333;")
        lines.append("    classDef unknown stroke-dasharray: 5 5;")

        groups = {
            "Sources": [],
            "Staging": [],
            "Transformations": [],
            "Outputs": [],
            "Other": []
        }

        for node_id, data in self.graph.nodes(data=True):
            ntype = data.get("type", "unknown")
            node_lines = []
            if ntype == "data":
                node_obj = self.data_nodes.get(node_id)
                role = node_obj.role.value if node_obj and node_obj.role else "unknown"
                node_lines.append(f'        {node_id}[("{node_id}<br/>[{role}]")]')
                if role == "SOURCE": 
                    node_lines.append(f"        class {node_id} source")
                    groups["Sources"].extend(node_lines)
                elif role == "TERMINAL": 
                    node_lines.append(f"        class {node_id} terminal")
                    groups["Outputs"].extend(node_lines)
                elif role == "INTERMEDIATE": 
                    node_lines.append(f"        class {node_id} intermediate")
                    groups["Staging"].extend(node_lines)
                else:
                    groups["Other"].extend(node_lines)
            elif ntype == "transformation":
                node_lines.append(f"        {node_id}[/ {node_id} /]")
                node_lines.append(f"        class {node_id} trans")
                groups["Transformations"].extend(node_lines)
            elif ntype == "module":
                node_lines.append(f'        {node_id}["{node_id}"]')
                groups["Other"].extend(node_lines)
            else:
                node_lines.append(f'        {node_id}{{{{{node_id}}}}}')
                node_lines.append(f"        class {node_id} unknown")
                groups["Other"].extend(node_lines)

        for group_name, group_lines in groups.items():
            if group_lines:
                lines.append(f"    subgraph {group_name}")
                lines.extend(group_lines)
                lines.append("    end")
                
        for u, v, data in self.graph.edges(data=True):
            etype = data.get("type", "edge")
            confidence = data.get("confidence_score", 1.0)
            if confidence < 0.5:
                lines.append(f"    {u} -. {etype} (heuristic) .-> {v}")
            else:
                lines.append(f"    {u} -- {etype} --> {v}")
            
        return "\n".join(lines)
