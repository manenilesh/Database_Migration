import pymysql

import psycopg2



def migrate_mysql_to_psql(mysql_config, psql_config, table_mapping=None):

    """

    Migrates data from MySQL to PostgreSQL.



    Args:

        mysql_config (dict): MySQL connection parameters (host, user, password, database).

        psql_config (dict): PostgreSQL connection parameters (host, user, password, database).

        table_mapping (dict, optional): A dictionary specifying table mappings.

                                         Keys: MySQL table names.

                                         Values: PostgreSQL table names.

                                         If None, all tables are migrated with the same names.

    """



    try:

        # Connect to MySQL

        mysql_conn = pymysql.connect(**mysql_config)

        mysql_cursor = mysql_conn.cursor()



        # Connect to PostgreSQL

        psql_conn = psycopg2.connect(**psql_config)

        psql_cursor = psql_conn.cursor()



        # Get list of tables from MySQL

        mysql_cursor.execute("SHOW TABLES")

        mysql_tables = [table[0] for table in mysql_cursor.fetchall()]



        for mysql_table in mysql_tables:

            psql_table = table_mapping.get(mysql_table, mysql_table) if table_mapping else mysql_table



            # Get column information from MySQL

            mysql_cursor.execute(f"DESCRIBE {mysql_table}")

            mysql_columns = mysql_cursor.fetchall()

            psql_columns = []

            for col in mysql_columns:

                col_name = col[0]

                col_type = col[1].upper()

                #Basic datatype mapping, add more mapping as needed.

                if "INT" in col_type:

                    psql_type = "INTEGER"

                elif "VARCHAR" in col_type:

                    psql_type = f"VARCHAR({col[1].split('(')[1].split(')')[0]})"

                elif "TEXT" in col_type:

                    psql_type = "TEXT"

                elif "DATE" in col_type:

                    psql_type = "DATE"

                elif "DATETIME" in col_type:

                    psql_type = "TIMESTAMP"

                elif "DECIMAL" in col_type:

                    psql_type = "DECIMAL"

                else:

                    psql_type = "TEXT" #Default to text.



                psql_columns.append(f"{col_name} {psql_type}")



            # Create table in PostgreSQL

            try:

                psql_cursor.execute(f"CREATE TABLE {psql_table} ({', '.join(psql_columns)})")

                psql_conn.commit()

            except psycopg2.errors.DuplicateTable:

                print(f"Table {psql_table} already exists. Skipping creation.")



            # Fetch data from MySQL

            mysql_cursor.execute(f"SELECT * FROM {mysql_table}")

            rows = mysql_cursor.fetchall()



            # Insert data into PostgreSQL

            for row in rows:

                placeholders = ", ".join(["%s"] * len(row))

                try:

                    psql_cursor.execute(f"INSERT INTO {psql_table} VALUES ({placeholders})", row)

                    psql_conn.commit()

                except psycopg2.errors.UniqueViolation:

                    print(f"Unique violation on table {psql_table}, row: {row}")

                    psql_conn.rollback() #rollback the transaction on unique violation.

                except Exception as e:

                    print(f"Error inserting row: {row}, Error: {e}")

                    psql_conn.rollback() #rollback on other errors.



        print("Migration completed successfully.")



    except pymysql.Error as err:

        print(f"MySQL error: {err}")

    except psycopg2.Error as err:

        print(f"PostgreSQL error: {err}")

    except Exception as err:

        print(f"General Error: {err}")

    finally:

        if 'mysql_conn' in locals() and mysql_conn.is_connected():

            mysql_cursor.close()

            mysql_conn.close()

        if 'psql_conn' in locals() and psql_conn.closed == 0:

            psql_cursor.close()

            psql_conn.close()



# Example usage:

mysql_config = {

    "host": "localhost",

    "user": "SQL_User",

    "password": "Pass@123",

    "database": "Motu"

}



psql_config = {

    "host": "100.100.100.100",  ##ip

    "user": "PSQL_User",

    "password": "Pass@123",
    

    "database": "patlu"

}



table_mapping = {

    "old_table_name": "new_table_name" #optional table name change.

}



migrate_mysql_to_psql(mysql_config, psql_config, table_mapping)
