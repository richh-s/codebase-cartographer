import sys
from codebase_cartographer.analyzers.sql_lineage_analyzer import SQLLineageAnalyzer
from sqlglot import parse_one, exp
from sqlglot.optimizer.qualify import qualify

analyzer = SQLLineageAnalyzer()
filepath = "/Users/aman/Desktop/projects/10academy/jaffle-shop-classic/models/customers.sql"
with open(filepath, "r") as f:
    sql = f.read()

mocked_sql = analyzer._mock_jinja(sql)
print("Mocked SQL:", mocked_sql)
try:
    expression = parse_one(mocked_sql, read="duckdb")
    qualified = qualify(expression, validate_qualify_columns=False)
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
