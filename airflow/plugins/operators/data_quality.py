from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

from helpers import SqlQueries

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 redshift_table_names,
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.table_names = redshift_table_names

    def execute(self, context):
        redshift_hook = PostgresHook("redshift")
        for table_name in self.table_names:
            records = redshift_hook.get_records(SqlQueries.count_rows.format(table_name=table_name))

            if len(records) < 1 or len(records[0]) < 1:
                raise ValueError(f"Data quality check failed. {table_name} returned no results")
            num_records = records[0][0]
            if num_records < 1:
                raise ValueError(f"Data quality check failed. {table_name} contained 0 rows")

            self.log.info(f"Data quality on table {table_name} check passed with {records[0][0]} records")
        
        
