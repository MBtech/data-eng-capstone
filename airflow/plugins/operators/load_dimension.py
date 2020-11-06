from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from helpers import SqlQueries

class LoadDimensionOperator(BaseOperator):

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 redshift_table_name,
                 sql_load_dim_statement,
                 delete_load_flag=True,
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.table_name=redshift_table_name
        self.sql_statement=sql_load_dim_statement
        self.delete_load_flag=delete_load_flag

    def execute(self, context):
        redshift = PostgresHook(postgres_conn_id="redshift")
        
        if self.delete_load_flag:
            sql_delete_table = SqlQueries.truncate_table.format(table_name=self.table_name)
        
        sql_load_dim = self.sql_statement.format(table_name=self.table_name)
        redshift.run(sql_load_dim)
#         self.log.info('LoadDimensionOperator not implemented yet')
