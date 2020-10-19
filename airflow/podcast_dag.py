from airflow import DAG
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from datetime import datetime


args = {
    'owner': 'airflow',
    'start_date': datetime(2020, 10, 18)
    'email': ['jordan.palamos@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 4,
}

dag = DAG('spark_job', default_args=args, schedule_interval="0 */4 * * *")


download = SparkSubmitOperator(
    task_id='spark_download',
    application='/home/ubuntu/src/download_mp3.py',
    conf={'packages':'org.apache.hadoop:hadoop-aws:2.7.3'},
    dag=dag,
)

transcribe = SparkSubmitOperator(
    task_id='spark_transcribe',
    application='/home/ubuntu/src/transcribe_S3_to_ES_v3.py',
    conf={'packages':'org.apache.hadoop:hadoop-aws:2.7.3'},
    dag=dag,
)
