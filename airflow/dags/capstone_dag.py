from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                                LoadDimensionOperator, DataQualityOperator, 
                                PreProcessAndLoadOperator, CalculateCorrelationOperator)

from helpers import SqlQueries

# AWS_KEY = os.environ.get('AWS_KEY')
# AWS_SECRET = os.environ.get('AWS_SECRET')
s3_bucketname = 'data-eng-capstone-udacity'

default_args = {
    'owner': 'udacity',
    'email_on_retry': False,
    'retries': 0,
    'start_date': datetime(2020, 10, 1),
    'depends_on_past': False
}

dag = DAG('capstone_dag',
          default_args=default_args,
          description='Analyze Covid tweets and cases',
          schedule_interval='@daily',
          catchup=False,
        )

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

stage_tweets_to_redshift = StageToRedshiftOperator(
    task_id='Stage_tweets',
    s3_input_loc='s3://data-eng-capstone-udacity/tweets/',
    redshift_table_name='staging_tweets',
    delimiter='\t',
    file_format='csv gzip',
    aws_credentials_id='aws_credentials',
    truncate=True,
    dag=dag
)

stage_covid_cases_to_redshift = StageToRedshiftOperator(
    task_id='Stage_covid_cases',
    s3_input_loc='s3://data-eng-capstone-udacity/cases/',
    redshift_table_name='staging_covid_cases',
    aws_credentials_id='aws_credentials',
    truncate=True,
    dag=dag
)

stage_country_codes_to_redshift = StageToRedshiftOperator(
    task_id='Load_country_codes',
    s3_input_loc='s3://data-eng-capstone-udacity/countries/country_code.csv',
    redshift_table_name='public.countries',
    aws_credentials_id='aws_credentials',
    truncate=True, 
    dag=dag
)

preprocess_and_load_to_redshift = PreProcessAndLoadOperator(
    task_id='Preprocess_and_load_redshift',
    redshift_table_name='staging_covid_cases',
    redshift_conn_id='redshift',
    dag=dag
)


load_covid_reactions_table = LoadFactOperator(
    task_id='Load_covid_reactions',
    redshift_table_name='covid_reactions',
    truncate=True,
    dag=dag
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    redshift_table_names = ['covid_reactions', 'countries'],
    dag=dag
)

calculate_correlation_task = CalculateCorrelationOperator(
    task_id='calculate_correlation',
    redshift_table_name='covid_reactions',
    s3_bucketname=s3_bucketname,
    dag=dag
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)

start_operator >> [stage_tweets_to_redshift, stage_country_codes_to_redshift] >> load_covid_reactions_table

start_operator >> stage_covid_cases_to_redshift >> preprocess_and_load_to_redshift >> load_covid_reactions_table

load_covid_reactions_table >> run_quality_checks >> calculate_correlation_task >> end_operator
