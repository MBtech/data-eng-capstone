from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from helpers import SqlQueries
import pandas as pd
from sqlalchemy import create_engine

class PreProcessAndLoadOperator(BaseOperator):

    ui_color = '#F98866'

    @apply_defaults
    def __init__(self,
                 redshift_table_name,
                 redshift_conn_id='redshift',
                 month_name = 'October',
                 truncate=True,
                 *args, **kwargs):

        super(PreProcessAndLoadOperator, self).__init__(*args, **kwargs)
        self.table_name=redshift_table_name
        self.redshift_conn_id = redshift_conn_id
        self.truncate = truncate
        self.month_name = month_name

    def execute(self, context):
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        
        df = redshift.get_pandas_df(SqlQueries.select_from_table.format(table_name=self.table_name))

        df = df.sort_values(['country', 'date'])
        df['confirmed'] = df.groupby(['country'])['confirmed'].diff().fillna(0)
        df['recovered'] = df.groupby(['country'])['recovered'].diff().fillna(0)
        df['deaths'] = df.groupby(['country'])['deaths'].diff().fillna(0)
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['date'].dt.month_name()== self.month_name]

        if self.truncate:
            redshift.run(SqlQueries.truncate_table.format(table_name="covid_cases"))

        rows = list(df.itertuples(index=False, name=None))
        redshift.insert_rows(table="covid_cases", rows=rows, commit_every=0)
        
