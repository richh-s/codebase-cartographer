
import pandas as pd
df = pd.read_csv("mock_project/stg_orders.csv")
df.to_parquet("s3://bucket/processed_orders.parquet")
