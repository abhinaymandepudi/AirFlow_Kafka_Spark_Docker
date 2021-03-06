
import airflow

from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.docker_operator import DockerOperator

args = {
    'owner': 'airflow',
    'description': 'spark Consumer via Docker Operator',
    'start_date': airflow.utils.dates.days_ago(1),       # this in combination with catchup=False ensures the DAG being triggered from the current date onwards along the set interval
    'provide_context': True,                            # this is set to True as we want to pass variables on from one task to another
}

dag = DAG(
    dag_id='flights_insight_DAG',
    default_args=args,
    schedule_interval='@daily',        # set interval,@once
    catchup=False,                    # indicate whether or not Airflow should do any runs for intervals between the start_date and the current date that haven't been run thus far
)


task2 = BashOperator(
     task_id='Entering_Docker_Operator',
     bash_command='echo "Now Starting a spark submit in different container"',
     dag=dag,
        )

task3 = DockerOperator(
    task_id = 'data_insight',
    image='Project_Flight_spark:latest',
    api_version='auto',
    auto_remove=True,
    volumes=['/usr/local/airflow/dags/src/spark_consume_data:/spark_consume_data'],
    command='/usr/spark/bin/spark-submit --master local[*] /spark_consume_data/data_insights.py',
    #docker_url='localhost:5000',
    network_mode='bridge',
    dag=dag,
)

task4 = BashOperator(
    task_id='Exiting_Docker_Operator',
    bash_command='echo "Back to original Airflow Container"',
    dag=dag,
)

task2 >> task3 >> task4       # set task priority
