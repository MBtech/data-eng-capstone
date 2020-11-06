from airflow.hooks.postgres_hook import PostgresHook
from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from helpers import SqlQueries

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'

    template_fields = ["s3_input_loc"]
    
    @apply_defaults
    def __init__(self,
                 s3_input_loc,
                 redshift_table_name,
                 aws_credentials_id,
                 delimiter=',',
                 file_format='csv',
                 truncate=False,
                 *args, **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.table_name = redshift_table_name
        self.s3_input_loc = s3_input_loc
        self.delimiter = delimiter
        self.format = file_format
        self.aws_credentials_id=aws_credentials_id
        self.truncate=truncate

    def execute(self, context):
        aws_hook = AwsHook("aws_credentials")
        credentials = aws_hook.get_credentials()
        
        redshift = PostgresHook(postgres_conn_id="redshift")
        
        if self.truncate:
            sql_cmd = SqlQueries.truncate_table.format(table_name=self.table_name)
            redshift.run(sql_cmd)

        sql_copy = SqlQueries.sql_copy_template.format(
                        table_name=self.table_name,
                        s3_input_loc=self.s3_input_loc,
                        access_key_id=credentials.access_key, 
                        secret_access_key=credentials.secret_key,
                        delimiter=self.delimiter,
                        format=self.format
                        )
        redshift.run(sql_copy)





