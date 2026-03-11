import os
import pytest
from codebase_cartographer.analyzers.python_dataflow_analyzer import PythonDataFlowAnalyzer

def test_python_dataflow_pandas(tmp_path):
    f = tmp_path / "test_pandas.py"
    f.write_text("""
import pandas as pd
BASE = "s3://bucket"
df = pd.read_csv(f"{BASE}/data.csv")
df.to_parquet("output.parquet")
    """)
    
    analyzer = PythonDataFlowAnalyzer()
    edges = analyzer.analyze(str(f), "test_module")
    
    # We expect 'data.csv' (from f-string) and 'output.parquet'
    # Note: our f-string resolution is currently heuristic/literal for content
    sources = [e.source for e in edges]
    targets = [e.target for e in edges]
    
    assert any("data.csv" in s for s in sources)
    assert any("output.parquet" in s for s in targets)

def test_python_dataflow_sqlalchemy(tmp_path):
    f = tmp_path / "test_sql.py"
    f.write_text("""
from sqlalchemy import create_engine
engine = create_engine("postgresql://localhost/db")
engine.execute("SELECT * FROM users JOIN orders ON users.id = orders.user_id")
    """)
    
    analyzer = PythonDataFlowAnalyzer()
    edges = analyzer.analyze(str(f), "test_module")
    
    # Expect postgres:users and postgres:orders (prefixed by engine dialect)
    sources = [e.source for e in edges]
    assert "postgresql:users" in sources
    assert "postgresql:orders" in sources
    assert any(e.type == "PYTHON_READ" for e in edges)

def test_python_dataflow_pyspark(tmp_path):
    f = tmp_path / "test_spark.py"
    f.write_text("""
df = spark.read.parquet("s3://input/data")
df.write.mode("overwrite").save("s3://output/results")
    """)
    
    analyzer = PythonDataFlowAnalyzer()
    edges = analyzer.analyze(str(f), "test_module")
    
    sources = [e.source for e in edges]
    targets = [e.target for e in edges]
    
    assert "s3://input/data" in sources
    assert "s3://output/results" in targets
    assert any(e.type == "PYTHON_READ" for e in edges)
    assert any(e.type == "PYTHON_WRITE" for e in edges)
