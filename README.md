MySQL to PostgreSQL Database Migration Script

This README provides comprehensive instructions for setting up MySQL and PostgreSQL databases, installing necessary tools and Python packages, and using the provided Python script to migrate data from a MySQL database to a PostgreSQL database.

Table of Contents

    Introduction
    Prerequisites
    Setup Instructions
        Install MySQL Server
        Install PostgreSQL Server
        Install PGAdmin (Optional)
        Install Python Packages
    Database Configuration
        Configure MySQL
        Configure PostgreSQL
    Python Migration Script
        Script Overview
        Usage
        Example Configuration
    Important Notes



1. Introduction
This Python script facilitates the migration of data from a MySQL database to a PostgreSQL database. It connects to both databases, retrieves table schemas and data from MySQL, and then creates corresponding tables and inserts data into PostgreSQL. It includes basic data type mapping and handles duplicate table creation and unique constraint violations during data insertion.


2. Prerequisites
Before you begin, ensure you have the following installed on your system:

    Operating System: A Linux distribution (e.g., Ubuntu) is assumed for the apt commands.
    MySQL Server: The source database.
    PostgreSQL Server: The destination database.
    pgAdmin: (Optional) A popular open-source administration and development platform for PostgreSQL.
    Python 3: The script is written in Python 3.
    Python Packages: PyMySQL and psycopg2-binary.



3. Setup Instructions
Follow these steps to set up your environment:
Install MySQL Server

sudo apt install mysql-server

Install PostgreSQL Server

sudo apt install curl ca-certificates
sudo install -d /usr/share/postgresql-common/pgdg
sudo curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc
sudo sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
sudo apt update
sudo apt -y install postgresql

Install PGAdmin (Optional)

curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg
sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list && apt update'
sudo apt install pgadmin4
sudo /usr/pgadmin4/bin/setup-web.sh

Install Python Packages

pip install PyMySQL psycopg2-binary



4. Database Configuration
Configure MySQL

    Secure Installation:

    sudo mysql_secure_installation

    Follow the prompts to set a root password, remove anonymous users, disallow remote root login, remove test database, and reload privilege tables.
    Create MySQL User and Database:

    sudo mysql -u root -p # Enter root password when prompted

    Inside the MySQL shell:

    CREATE USER 'SQL_User'@'localhost' IDENTIFIED BY 'Pass@123';
    GRANT ALL PRIVILEGES ON *.* TO 'SQL_User'@'localhost';
    FLUSH PRIVILEGES;
    EXIT;

    Note: The SQL_User is configured for localhost access. If your MySQL database is on a different host, adjust 'SQL_User'@'localhost' accordingly.
    Test MySQL User and Create Database:

    sudo mysql -u SQL_User -p # Enter 'Pass@123' when prompted

    Inside the MySQL shell:

    CREATE DATABASE oggy;
    USE oggy;
    -- You can create tables here for testing, e.g.:
    -- CREATE TABLE example_table (id INT PRIMARY KEY, name VARCHAR(255));
    -- INSERT INTO example_table VALUES (1, 'Test Data');
    EXIT;

Configure PostgreSQL

    Access PostgreSQL Shell:

    sudo -i -u postgres
    psql

    Create PostgreSQL User and Database: Inside the psql shell:

    CREATE USER PSQL_User WITH LOGIN PASSWORD 'Pass@123';
    ALTER USER PSQL_User WITH SUPERUSER; -- Grant superuser for ease of migration, adjust permissions as needed for production.
    \du -- To list users and verify
    CREATE DATABASE patlu;
    \l -- To list databases and verify
    \c patlu; -- Connect to the new database
    -- You can create tables here for testing, e.g.:
    -- CREATE TABLE example_psql_table (id INTEGER PRIMARY KEY, name VARCHAR(255));
    EXIT;

    Then exit the postgres user session:

    exit

    Edit PostgreSQL Configuration Files (for remote access, if needed): If your PostgreSQL server is not on localhost or you need to access it from a different machine, you'll need to adjust its configuration.
        postgresql.conf:

        sudo nano /etc/postgresql/17/main/postgresql.conf

        Find the line listen_addresses = 'localhost' and change it to the IP address of your PostgreSQL server, or '*' to listen on all interfaces. Example:

        listen_addresses = '100.100.100.100' # Replace with your server's IP or '*'

        pg_hba.conf:

        sudo nano /etc/postgresql/17/main/pg_hba.conf

        Add or modify a line to allow connections from your migration script's host. For example, to allow connections from the 100.100.100.0/24 network for all databases and users using md5 password authentication:

        # TYPE  DATABASE        USER            ADDRESS                 METHOD
        host    all             all             100.100.100.100/24        md5

        Note: 100.100.100.00/24 is an example. Replace it with the network range from which your migration script will connect, or 0.0.0.0/0 for any IP (less secure).
    Restart PostgreSQL Service: After modifying configuration files, you must restart PostgreSQL for changes to take effect:

    sudo systemctl restart postgresql



5. Python Migration Script
Script Overview
The migrate_mysql_to_psql function handles the core migration logic:

    mysql_config (dict): Connection parameters for the MySQL database (host, user, password, database).
    psql_config (dict): Connection parameters for the PostgreSQL database (host, user, password, database).
    table_mapping (dict, optional): A dictionary to rename tables during migration. Keys are MySQL table names, and values are desired PostgreSQL table names. If None, tables retain their original names.

The script performs the following for each table in MySQL:

    Fetches table schema from MySQL.
    Maps MySQL data types to PostgreSQL data types (basic mapping is provided; extend as needed).
    Creates the corresponding table in PostgreSQL.
    Fetches all data from the MySQL table.
    Inserts data into the PostgreSQL table row by row.
    Includes basic error handling for connection issues, duplicate table creation, and unique constraint violations during insertion.

Usage

    Save the provided Python code as a .py file (e.g., migrate.py).
    Update the mysql_config and psql_config dictionaries with your database credentials and details.
    Optionally, define table_mapping if you need to rename tables during migration.
    Run the script from your terminal.

Example Configuration

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
# Extract length from VARCHAR(N)
try:
length = col[1].split('(')[1].split(')')[0]
psql_type = f"VARCHAR({length})"
except IndexError:
psql_type = "VARCHAR" # Fallback if length not found
elif "TEXT" in col_type:
psql_type = "TEXT"
elif "DATE" in col_type:
psql_type = "DATE"
elif "DATETIME" in col_type:
psql_type = "TIMESTAMP"
elif "DECIMAL" in col_type or "NUMERIC" in col_type:
psql_type = "NUMERIC" # PostgreSQL uses NUMERIC for arbitrary precision
elif "FLOAT" in col_type:
psql_type = "REAL" # Single precision float
elif "DOUBLE" in col_type:
psql_type = "DOUBLE PRECISION" # Double precision float
elif "BOOLEAN" in col_type or "TINYINT(1)" in col_type: # MySQL TINYINT(1) often maps to boolean
psql_type = "BOOLEAN"
else:
psql_type = "TEXT" #Default to text for unhandled types

psql_columns.append(f"{col_name} {psql_type}")

# Create table in PostgreSQL
try:
psql_cursor.execute(f"CREATE TABLE {psql_table} ({', '.join(psql_columns)})")
psql_conn.commit()
print(f"Table {psql_table} created in PostgreSQL.")
except psycopg2.errors.DuplicateTable:
print(f"Table {psql_table} already exists. Skipping creation.")
except Exception as e:
print(f"Error creating table {psql_table}: {e}")
psql_conn.rollback()


# Fetch data from MySQL
mysql_cursor.execute(f"SELECT * FROM {mysql_table}")
rows = mysql_cursor.fetchall()

# Insert data into PostgreSQL
if rows: # Only proceed if there are rows to insert
placeholders = ", ".join(["%s"] * len(rows[0]))
for row in rows:
try:
psql_cursor.execute(f"INSERT INTO {psql_table} VALUES ({placeholders})", row)
psql_conn.commit()
except psycopg2.errors.UniqueViolation:
print(f"Unique violation on table {psql_table}, row: {row}. Skipping insertion for this row.")
psql_conn.rollback() #rollback the transaction on unique violation.
except Exception as e:
print(f"Error inserting row: {row}, Error: {e}. Rolling back transaction.")
psql_conn.rollback() #rollback on other errors.
else:
print(f"No data found in MySQL table {mysql_table} to migrate.")

print("Migration completed successfully.")

except pymysql.Error as err:
print(f"MySQL error: {err}")
except psycopg2.Error as err:
print(f"PostgreSQL error: {err}")
except Exception as err:
print(f"General Error: {err}")
finally:
if 'mysql_conn' in locals() and mysql_conn.open: # Check if connection is open for pymysql
mysql_cursor.close()
mysql_conn.close()
print("MySQL connection closed.")
if 'psql_conn' in locals() and not psql_conn.closed: # Check if connection is not closed for psycopg2
psql_cursor.close()
psql_conn.close()
print("PostgreSQL connection closed.")

# Example usage:
mysql_config = {
"host": "localhost",
"user": "SQL_User",
"password": "Pass@123",
"database": "oggy" # Replace with your MySQL database name
}

psql_config = {
"host": "100.100.100.100",  # Replace with your PostgreSQL server IP or 'localhost'
"user": "PSQL_User",
"password": "Pass@123",
"database": "patlu" # Replace with your PostgreSQL database name
}

# Optional: Define table mapping if you want to rename tables
table_mapping = {
# "mysql_old_table_name": "psql_new_table_name",
# "another_mysql_table": "different_psql_table"
}

if __name__ == "__main__":
migrate_mysql_to_psql(mysql_config, psql_config, table_mapping)



6. Important Notes

    Data Type Mapping: The script provides a basic mapping of common MySQL data types to PostgreSQL. For complex or custom data types, you might need to extend the if/elif conditions within the script to ensure accurate type conversion.
    Primary Keys and Constraints: The current script only creates tables based on column names and types. It does not automatically migrate primary key constraints, foreign key constraints, indexes, or default values. You will need to add these manually to the PostgreSQL tables after the initial migration, or enhance the script to extract and apply these constraints.
    Error Handling: The script includes try-except blocks for common database errors and unique constraint violations. In case of a UniqueViolation, the specific row causing the issue is skipped, and the transaction is rolled back for that row to maintain data integrity. Other errors will also cause a rollback for the current transaction.
    PostgreSQL listen_addresses and pg_hba.conf: Remember to configure these files correctly if your PostgreSQL server is not on the same machine as the script or if you need to allow external connections. Always restart the PostgreSQL service after making changes to these files.
    Security: For production environments, avoid using SUPERUSER for the PSQL_User and ensure that the pg_hba.conf entries are as restrictive as possible (e.g., specifying exact IP addresses instead of broad network ranges).
    Large Datasets: For very large databases, row-by-row insertion might be slow. Consider using PostgreSQL's COPY command or other bulk import methods for better performance, which would require a more advanced script.
    Table Existence: The script checks if a table already exists in PostgreSQL and skips its creation if it does. This prevents errors if you run the script multiple times.
