from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from helpers import SqlQueries

from airflow.hooks.S3_hook import S3Hook

class CalculateCorrelationOperator(BaseOperator):

    ui_color = '#F98866'

    @apply_defaults
    def __init__(self,
                 redshift_table_name,
                 redshift_conn_id='redshift',
                 s3_filename='correlation_matrix.csv',
                 s3_bucketname='data-eng-capstone-udacity',
                 s3_conn_id="S3_conn",
                 *args, **kwargs):

        super(CalculateCorrelationOperator, self).__init__(*args, **kwargs)
        self.table_name=redshift_table_name
        self.redshift_conn_id = redshift_conn_id
        self.s3_filename=s3_filename
        self.s3_bucketname = s3_bucketname
        self.s3_conn_id=s3_conn_id

    def execute(self, context):
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        df = redshift.get_pandas_df(SqlQueries.select_from_table.format(table_name=self.table_name))

        df = df[df['country'].notnull()]
        df = df.sort_values(['country', 'date'])

        df = df[['country', 'date', 'confirmed', 'number_of_tweets', 'recovered', 'deaths']]
        df_corr = df.groupby(['country']).corr()

        flat_corr = df_corr.reset_index().rename(columns={'level_1':'parameter'})

        flat_corr.to_csv(self.s3_filename)

        hook = S3Hook(aws_conn_id=self.s3_conn_id)
        hook.load_file(self.s3_filename, self.s3_filename, self.s3_bucketname)



