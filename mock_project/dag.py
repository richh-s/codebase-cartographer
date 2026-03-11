
from airflow import DAG
with DAG('test_dag') as dag:
    stg_orders >> process_orders
