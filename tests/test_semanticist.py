import pytest
from unittest.mock import MagicMock, patch
from models.nodes import ModuleNode
from agents.semanticist import SemanticistAgent
from utils.llm_client import LLMClient

@pytest.fixture
def mock_llm():
    client = MagicMock(spec=LLMClient)
    client.budget = MagicMock()
    client.budget.can_afford_batch.return_value = True
    client.budget.modules_eligible = 0
    client.budget.modules_processed = 0
    return client

def test_semantic_analysis_flow(mock_llm):
    # Setup
    agent = SemanticistAgent(llm_client=mock_llm)
    modules = [
        ModuleNode(identity="m1.py", path="m1.py", language="py"),
        ModuleNode(identity="m2.py", path="m2.py", language="py"),
        ModuleNode(identity="m3.py", path="m3.py", language="py"),
        ModuleNode(identity="m4.py", path="m4.py", language="py"),
    ]
    
    # Mock Purposes
    mock_llm.get_purpose_statements.return_value = [
        {"module_path": "m1.py", "purpose_statement": "Purpose 1", "purpose_confidence": 0.9},
        {"module_path": "m2.py", "purpose_statement": "Purpose 2", "purpose_confidence": 0.8},
        {"module_path": "m3.py", "purpose_statement": "Purpose 3", "purpose_confidence": 0.7},
        {"module_path": "m4.py", "purpose_statement": "Purpose 4", "purpose_confidence": 0.9},
    ]
    
    # Mock Embeddings
    mock_llm.embed_texts.return_value = [[0.1]*768] * 4
    
    # Mock Cluster Labeling
    mock_llm._call_with_retry.return_value = '{"domain_name": "Mapped Domain"}'
    
    # Execute
    agent.analyze_modules(modules)
    
    # Assert
    assert modules[0].purpose_statement == "Purpose 1"
    assert modules[0].domain_cluster == "Mapped Domain"
    assert mock_llm.get_purpose_statements.called
    assert mock_llm.embed_texts.called

def test_drift_detection(mock_llm):
    agent = SemanticistAgent(llm_client=mock_llm)
    module = ModuleNode(identity="drift.py", path="drift.py", language="py")
    module.purpose_statement = "High level purpose"
    
    # Mock summary with docstring
    with patch("agents.semanticist.build_module_summary") as mock_summary:
        mock_summary.return_value = {"docstring": "Different implementation detail docstring"}
        
        # Mock embeddings that are very different
        mock_llm.embed_texts.return_value = [[1.0, 0.0], [0.0, 1.0]] # Cosine similarity 0
        
        agent._detect_drift(module)
        
        assert module.documentation_drift is True # 0 < 0.65

def test_low_confidence_exclusion(mock_llm):
    agent = SemanticistAgent(llm_client=mock_llm)
    modules = [
        ModuleNode(identity="low.py", path="low.py", language="py"),
        ModuleNode(identity="high1.py", path="high1.py", language="py"),
        ModuleNode(identity="high2.py", path="high2.py", language="py"),
        ModuleNode(identity="high3.py", path="high3.py", language="py"),
        ModuleNode(identity="high4.py", path="high4.py", language="py"),
    ]
    
    # Mock Purposes - MUST MATCH ALPHABETICAL ORDER (high1, high2, high3, high4, low)
    mock_llm.get_purpose_statements.return_value = [
        {"module_path": "high1.py", "purpose_statement": "P", "purpose_confidence": 0.9},
        {"module_path": "high2.py", "purpose_statement": "P", "purpose_confidence": 0.9},
        {"module_path": "high3.py", "purpose_statement": "P", "purpose_confidence": 0.9},
        {"module_path": "high4.py", "purpose_statement": "P", "purpose_confidence": 0.9},
        {"module_path": "low.py", "purpose_statement": "P", "purpose_confidence": 0.4},
    ]
    
    mock_llm.embed_texts.return_value = [[0.1]*2] * 4 # Only 4 high confidence
    
    agent.analyze_modules(modules)
    
    low_module = next(m for m in modules if m.identity == "low.py")
    assert low_module.domain_cluster == "Unclassified"
