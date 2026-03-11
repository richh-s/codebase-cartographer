import os
import json
import pytest
from codebase_cartographer.agents.surveyor import SurveyorAgent

def test_surveyor_negative_dead_code(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    
    # 1. Hub file
    hub = repo_dir / "hub.py"
    hub.write_text("def main(): pass")
    
    # 2. Sink file (in models dir)
    models_dir = repo_dir / "models"
    models_dir.mkdir()
    sink = models_dir / "final_output.sql"
    sink.write_text("select * from {{ ref('hub') }}")
    
    # 3. Junk Module (dead code candidate)
    junk = repo_dir / "junk_module.py"
    junk.write_text("def unused(): pass")
    
    # Run agent
    agent = SurveyorAgent(str(repo_dir))
    out_file = str(repo_dir / "module_graph.json")
    agent.run(out_file)
    
    assert os.path.exists(out_file)
    with open(out_file, 'r') as f:
        data = json.load(f)
        
    nodes = {n['identity']: n for n in data['nodes']}
    
    # Negative Test: Junk should be dead code
    assert "junk_module.py" in nodes
    assert nodes["junk_module.py"]["is_dead_code_candidate"] is True
    
def test_surveyor_phase1_5_features(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    
    # 1. Hub file
    hub = repo_dir / "hub.py"
    hub.write_text("def main(): pass")
    
    # 2. SQL File with complexity and a macro call
    models_dir = repo_dir / "models"
    models_dir.mkdir()
    sql_model = models_dir / "complex_query.sql"
    sql_model.write_text("""
        with cte as (select * from {{ ref('hub') }})
        select * from cte
        left join {{ source('raw', 'data') }} on a = b
        where case when c = 1 then true else false end
        group by 1
        -- macro call
        {{ generate_surrogate_key(['id', 'name']) }}
    """)
    
    # 3. Meta File
    readme = repo_dir / "README.md"
    readme.write_text("# Project")
    
    # Run agent
    agent = SurveyorAgent(str(repo_dir))
    out_file = str(repo_dir / "module_graph.json")
    agent.run(out_file)
    
    with open(out_file, 'r') as f:
        data = json.load(f)
        
    nodes = {n['identity']: n for n in data['nodes']}
    
    # Test Informational Isolation
    assert "README.md" in nodes
    meta_node = nodes["README.md"]
    assert meta_node["is_informational"] is True
    assert meta_node["architecture_layer"] == "meta"
    assert "README.md" not in data["top_hubs"]
    
    # Test Architectural layer
    sql_node = nodes["models/complex_query.sql"]
    assert sql_node["architecture_layer"] == "product"
    
    # Test SQL Complexity
    # has 1 WITH, 1 JOIN, 1 CASE, 1 GROUP BY = at least 3.0
    assert sql_node["complexity_score"] >= 3.0
    
    # Test Importance Rank (Min Max Normalized)
    assert 1 <= sql_node["importance_score"] <= 100
    
    # Test Edge Metadata exists
    assert len(data["edges"]) > 0
    # Edges are now structured dictionaries {"source": s, "target": t, "type": type}
    edge_types = [e.get("type") for e in data["edges"] if isinstance(e, dict) and "type" in e]
    assert len(edge_types) > 0
