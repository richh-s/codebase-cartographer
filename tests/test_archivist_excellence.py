import os
import json
import pytest
import shutil
from orchestrator import Orchestrator
from utils.git_provider import GitProvider
from utils.trace_logger import TraceLogger

@pytest.fixture
def repo_path(tmp_path):
    # Setup a mock repo structure
    repo = tmp_path / "mock-repo"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "a.py").write_text("def a(): pass")
    (repo / "src" / "b.py").write_text("import a\ndef b(): a.a()")
    
    # Initialize mock git
    os.system(f"cd {repo} && git init && git add . && git commit -m 'init' --author='Test Author <test@example.com>'")
    return str(repo)

def test_artifact_metadata_header(repo_path):
    orchestrator = Orchestrator(repo_path)
    orchestrator.run_analysis(llm_enabled=False)
    
    artifacts_dir = os.path.join(repo_path, "artifacts")
    assert os.path.exists(artifacts_dir)
    
    files = os.listdir(artifacts_dir)
    m_graph_file = [f for f in files if f.startswith("module_graph_git_")][0]
    
    with open(os.path.join(artifacts_dir, m_graph_file), "r") as f:
        data = json.load(f)
        assert data["schema_version"] == "1.0"
        assert "git_commit" in data
        assert "timestamp" in data
        assert data["analysis_version"] == "cartographer_phase4"

def test_relative_paths(repo_path):
    orchestrator = Orchestrator(repo_path)
    orchestrator.run_analysis(llm_enabled=False)
    
    artifacts_dir = os.path.join(repo_path, "artifacts")
    files = os.listdir(artifacts_dir)
    m_graph_file = [f for f in files if f.startswith("module_graph_git_")][0]
    
    with open(os.path.join(artifacts_dir, m_graph_file), "r") as f:
        data = json.load(f)
        for node in data.get("nodes", []):
            # Identity/Path should be relative (no leading slash)
            assert not node["path"].startswith("/")
            assert not node["identity"].startswith("/")

def test_ast_hash_stability(repo_path):
    orchestrator = Orchestrator(repo_path)
    
    # 1. First run
    orchestrator.run_analysis(llm_enabled=False)
    # The cache stores relative paths
    initial_hash = orchestrator.cache["files"]["src/a.py"]
    
    # 2. Modify a.py with comments only
    with open(os.path.join(repo_path, "src", "a.py"), "a") as f:
        f.write("\n# This is a comment change")
    
    # 3. Second run
    orchestrator.run_analysis(llm_enabled=False)
    new_hash = orchestrator.cache["files"]["src/a.py"]
    
    assert initial_hash == new_hash, "AST hash should be stable across comment changes"

def test_deterministic_export(repo_path):
    orchestrator = Orchestrator(repo_path)
    
    # Run once
    orchestrator.run_analysis(llm_enabled=False)
    artifacts_dir = os.path.join(repo_path, "artifacts")
    m_graph_file_1 = [f for f in os.listdir(artifacts_dir) if f.startswith("module_graph_git_")][0]
    with open(os.path.join(artifacts_dir, m_graph_file_1), "r") as f:
        data_1 = json.load(f)
        # Remove timestamp for comparison
        data_1.pop("timestamp")
        
    # Clear cache and artifacts and run again
    shutil.rmtree(os.path.join(repo_path, ".cartography"))
    shutil.rmtree(os.path.join(repo_path, "artifacts"))
    orchestrator = Orchestrator(repo_path) 
    orchestrator.run_analysis(llm_enabled=False)
    
    m_graph_file_2 = [f for f in os.listdir(artifacts_dir) if f.startswith("module_graph_git_")][0]
    with open(os.path.join(artifacts_dir, m_graph_file_2), "r") as f:
        data_2 = json.load(f)
        data_2.pop("timestamp")
        
    assert data_1 == data_2, f"Exports should be identical. Diff keys: {set(data_1.keys()) ^ set(data_2.keys())}"
