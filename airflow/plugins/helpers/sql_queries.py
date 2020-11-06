class SqlQueries:
    sql_copy_template = ("""copy {table_name} from '{s3_input_loc}'
                         credentials 'aws_access_key_id={access_key_id};aws_secret_access_key={secret_access_key}'
                         region 'us-west-2' 
                         NULL as 'NULL'
                         {format} 
                         IGNOREHEADER 1
                         delimiter '{delimiter}';
                       """)
    
    select_from_table = """
        SELECT * from {table_name};
    """

    covid_reactions_table_insert = """
        INSERT INTO {table_name} 
        SELECT 
            agg_tweets.number_of_tweets,
            agg_tweets.date,
            cases.country, 
            cases.confirmed, 
            cases.recovered, 
            cases.deaths
            FROM (SELECT countries.name as country, * 
                FROM (
                    SELECT count(staging_tweets.tweetid) as number_of_tweets,
                    staging_tweets.countrycode,
                    staging_tweets.date
                    FROM staging_tweets 
                    GROUP BY staging_tweets.countrycode, staging_tweets.date) tweets 
                LEFT JOIN countries
                ON tweets.countrycode = countries.countrycode) agg_tweets
            LEFT JOIN covid_cases cases
            ON cases.date=agg_tweets.date
                AND cases.country = agg_tweets.country;
                
    """

    truncate_table = ("""
        TRUNCATE TABLE {table_name}
    """)
    
    count_rows = ("""
       SELECT COUNT(*) FROM {table_name}
    """)