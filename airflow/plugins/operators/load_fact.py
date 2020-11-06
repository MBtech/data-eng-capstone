from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from helpers import SqlQueries


class LoadFactOperator(BaseOperator):

    ui_color = '#F98866'

    @apply_defaults
    def __init__(self,
                 redshift_table_name,
                 truncate=False,
                 *args, **kwargs):

        super(LoadFactOperator, self).__init__(*args, **kwargs)
        self.table_name=redshift_table_name
        self.truncate = truncate

    def execute(self, context):
        redshift = PostgresHook(postgres_conn_id="redshift")
        
        if self.truncate:
            redshift.run(SqlQueries.truncate_table.format(table_name=self.table_name))
        
        sql_load_fact = SqlQueries.covid_reactions_table_insert.format(table_name=self.table_name)
        redshift.run(sql_load_fact)