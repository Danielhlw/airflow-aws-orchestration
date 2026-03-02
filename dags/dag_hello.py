"""
DAG mínimo para validar que o Airflow está executando tasks.
Uma única task que imprime "Hello from Airflow".
"""
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="dag_hello",
    description="DAG de teste: uma task que imprime Hello",
    schedule=None,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["hello", "teste"],
) as dag:
    say_hello = BashOperator(
        task_id="say_hello",
        bash_command='echo "Hello from Airflow"',
    )
