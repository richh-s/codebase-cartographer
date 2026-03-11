import pytest
from codebase_cartographer.graph.lineage_graph import LineageGraph
from codebase_cartographer.models.lineage import DataNode, LineageEdge

def test_lineage_graph_impact_analysis():
    lg = LineageGraph()
    
    # Define nodes: A -> B -> C
    lg.add_data_node(DataNode(identity="node_a", name="node_a", canonical_name="node_a", namespace="test"))
    lg.add_data_node(DataNode(identity="node_b", name="node_b", canonical_name="node_b", namespace="test"))
    lg.add_data_node(DataNode(identity="node_c", name="node_c", canonical_name="node_c", namespace="test"))
    
    lg.add_lineage_edge(LineageEdge(source="node_a", target="node_b", type="TRANSFORM", origin_analyzer="test"))
    lg.add_lineage_edge(LineageEdge(source="node_b", target="node_c", type="TRANSFORM", origin_analyzer="test"))
    
    # Compute importance (A should be more important because it has more descendants)
    # Give base structural importance
    lg.compute_importance({"node_a": 10, "node_b": 5, "node_c": 1})
    
    # node_a importance should be > 10 (base 10 + impact factor)
    assert lg.data_nodes["node_a"].importance_score > 20 # Scaled factor applied in code
    assert lg.data_nodes["node_a"].importance_score > lg.data_nodes["node_b"].importance_score
    
    # Blast radius of A
    radius = lg.blast_radius("node_a")
    assert radius["downstream_count"] == 2
    assert any(n["id"] == "node_c" for n in radius["impacted_nodes"])

def test_lineage_graph_integrity():
    lg = LineageGraph()
    
    # Create a cycle: A -> B -> A
    lg.add_lineage_edge(LineageEdge(source="node_a", target="node_b", type="TRANSFORM", origin_analyzer="test"))
    lg.add_lineage_edge(LineageEdge(source="node_b", target="node_a", type="TRANSFORM", origin_analyzer="test"))
    
    warnings = lg.validate_integrity()
    assert any("Cycles" in w for w in warnings)
    assert any("undefined node" in w for w in warnings) # Since we didn't add data_nodes explicitly

def test_lineage_graph_sources_sinks():
    lg = LineageGraph()
    # A -> B
    lg.add_lineage_edge(LineageEdge(source="A", target="B", type="READ", origin_analyzer="test"))
    
    assert "A" in lg.find_sources()
    assert "B" in lg.find_sinks()
