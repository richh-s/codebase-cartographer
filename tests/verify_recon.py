import os
import json
from datetime import datetime
from unittest.mock import MagicMock
from src.orchestrator import Orchestrator
from models.nodes import ModuleNode
from models.lineage import DataNode

def verify_recon_generation():
    # Setup
    repo_path = os.getcwd()
    orchestrator = Orchestrator(repo_path)
    
    # Mock Semanticist
    orchestrator.semanticist = MagicMock()
    orchestrator.semanticist.answer_day_one_questions.return_value = "## Synthesis Results\n\nVerified Answer 1\nVerified Answer 2"
    
    # Mock Data
    modules = [
        ModuleNode(identity="m1.py", path="m1.py", language="py", purpose_statement="Purpose 1"),
        ModuleNode(identity="m2.py", path="m2.py", language="py", purpose_statement="Purpose 2")
    ]
    
    lineage_graph = MagicMock()
    lineage_graph.data_nodes = {"d1": DataNode(
        identity="d1", 
        name="d1", 
        canonical_name="d1", 
        namespace="public", 
        system="s1", 
        type="t1", 
        environment="production"
    )}
    lineage_graph.transformation_nodes = {}
    lineage_graph.graph = MagicMock()
    lineage_graph.graph.number_of_edges.return_value = 5
    
    # Execute
    orchestrator.generate_reconnaissance_report(modules, lineage_graph)
    
    # Verify file
    recon_path = os.path.join(repo_path, "RECONNAISSANCE.md")
    assert os.path.exists(recon_path)
    with open(recon_path, "r") as f:
        content = f.read()
        print(f"Generated RECONNAISSANCE.md content:\n{content}")
        assert "Verified Answer" in content
    
    # Cleanup
    # os.remove(recon_path)
    print("Verification of RECONNAISSANCE.md generation successful!")

if __name__ == "__main__":
    verify_recon_generation()
