import pytest
from codebase_cartographer.analyzers.sql_lineage_analyzer import SQLLineageAnalyzer

def test_sql_lineage_dbt_ref(tmp_path):
    f = tmp_path / "model.sql"
    f.write_text("""
    WITH raw_data AS (
        SELECT * FROM {{ ref('stg_orders') }}
    )
    SELECT * FROM raw_data
    """)
    
    analyzer = SQLLineageAnalyzer()
    edges = analyzer.analyze(str(f), "model")
    
    # Epect 1 edge from stg_orders to model
    assert len(edges) >= 1
    sources = [e.source for e in edges]
    assert "stg_orders" in sources
    assert any(e.type == "DBT_REF" for e in edges)

def test_sql_lineage_dbt_source(tmp_path):
    f = tmp_path / "model.sql"
    f.write_text("SELECT * FROM {{ source('raw', 'users') }}")
    
    analyzer = SQLLineageAnalyzer()
    edges = analyzer.analyze(str(f), "model")
    
    sources = [e.source for e in edges]
    assert "raw_users" in sources
    assert any(e.type == "DBT_SOURCE" for e in edges)

def test_sql_lineage_complex_cte(tmp_path):
    f = tmp_path / "complex.sql"
    f.write_text("""
    WITH a AS (SELECT * FROM table_a),
         b AS (SELECT * FROM a JOIN table_b ON a.id = b.id)
    SELECT * FROM b
    """)
    
    analyzer = SQLLineageAnalyzer()
    edges = analyzer.analyze(str(f), "complex")
    
    sources = [e.source for e in edges]
    # 'a' and 'b' are internal CTEs, should NOT be in sources if scope parsing is correct
    # Only table_a and table_b should be external sources
    assert "table_a" in sources
    assert "table_b" in sources
    assert "a" not in sources
    assert "b" not in sources

def test_sql_lineage_fallback(tmp_path):
    f = tmp_path / "bad.sql"
    # Malformed SQL that sqlglot might fail on
    f.write_text("SELECT FROM WHERE JOIN my_table")
    
    analyzer = SQLLineageAnalyzer()
    edges = analyzer.analyze(str(f), "bad")
    
    # Should use regex fallback
    assert any("my_table" in e.source for e in edges)
    assert any(e.confidence_score == 0.3 for e in edges)
