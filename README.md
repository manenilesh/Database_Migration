Database Installation and Migration Guide
This README provides a comprehensive guide for installing and setting up MySQL, PostgreSQL, and PGAdmin on an Ubuntu system. It also includes a Python script for migrating data from a MySQL database to a PostgreSQL database.
Table of Contents

    Prerequisites
    Installation and Setup
        MySQL Server
        PostgreSQL
        PGAdmin 4
    Python Database Connectors
    Database Configuration
        MySQL User and Database Setup
        PostgreSQL User and Database Setup
        PostgreSQL Remote Access Configuration
    Python Migration Script
    Usage
    Troubleshooting

1. Prerequisites

    An Ubuntu-based operating system (e.g., Ubuntu 20.04, 22.04).
    sudo privileges.
    Internet connectivity.

2. Installation and Setup
MySQL Server
To install the MySQL server, open your terminal and run:

sudo apt update
sudo apt install mysql-server

PostgreSQL
To install PostgreSQL, follow these steps to add the official PostgreSQL APT repository, which ensures you get the latest stable version:

sudo apt install curl ca-certificates
sudo install -d /usr/share/postgresql-common/pgdg
sudo curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc
sudo sh -c 'echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
sudo apt update
sudo apt -y install postgresql

PGAdmin 4
PGAdmin 4 is a popular graphical administration tool for PostgreSQL. Install it using the following commands:

curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg
sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list && sudo apt update'
sudo apt install pgadmin4

After installation, set up the web interface for PGAdmin 4:

sudo /usr/pgadmin4/bin/setup-web.sh

Follow the prompts to create an email and password for your PGAdmin 4 login. You can then access PGAdmin 4 by opening a web browser and navigating to http://127.0.0.1/pgadmin4 (or http://your_server_ip/pgadmin4).
3. Python Database Connectors
To interact with MySQL and PostgreSQL from Python, you need to install the respective database connector libraries.
PyMySQL
For MySQL connectivity:

pip install PyMySQL

Psycopg2-binary
For PostgreSQL connectivity:

pip install psycopg2-binary

4. Database Configuration
MySQL User and Database Setup
After installing MySQL, it's highly recommended to run the security script to improve its security posture:

sudo mysql_secure_installation

Follow the prompts to set a root password, remove anonymous users, disallow root login remotely, and remove the test database.
Now, log in to the MySQL root account to create a new user and database:

sudo mysql -u root -p # Enter the root password you set

Once in the MySQL prompt (mysql>), execute the following commands to create a user named SQL_User with a password Pass@123 and grant them all privileges:

CREATE USER 'SQL_User'@'localhost' IDENTIFIED BY 'Pass@123';
GRANT ALL PRIVILEGES ON *.* TO 'SQL_User'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SHOW GRANTS FOR 'SQL_User'@'localhost';

(Note: Using localhost for the user limits connections to the local machine. If you need remote access, replace localhost with % or a specific IP address.)
Exit MySQL:

exit;

Test logging in with the new user:

sudo mysql -u SQL_User -p

Enter Pass@123 when prompted for the password.
Inside the MySQL prompt, create a sample database:

CREATE DATABASE oggy;
USE oggy;
CREATE TABLE example_table (
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(255) NOT NULL,
value INT
);
INSERT INTO example_table (name, value) VALUES ('Test1', 10), ('Test2', 20);
SELECT * FROM example_table;

Exit MySQL:

exit;

PostgreSQL User and Database Setup
Switch to the postgres system user, which is the default superuser for PostgreSQL:

sudo -i -u postgres

Now, access the PostgreSQL prompt:

psql

Inside the PostgreSQL prompt (postgres=#), create a new user named PSQL_User with a password Pass@123 and grant them superuser privileges:

CREATE USER PSQL_User WITH LOGIN PASSWORD 'Pass@123';
ALTER USER PSQL_User WITH SUPERUSER;
\du # List users to verify

Create a sample database named jack:

CREATE DATABASE jack;
\l # List databases to verify

Exit PostgreSQL prompt:

\q

Exit postgres user session:

exit

PostgreSQL Remote Access Configuration
To allow remote connections to your PostgreSQL server, you need to modify two configuration files.
1. postgresql.conf: Edit the postgresql.conf file to change the listen_addresses. Replace localhost with the IP address of your PostgreSQL server or '*' to listen on all available network interfaces.

sudo nano /etc/postgresql/17/main/postgresql.conf # Adjust '17' to your PostgreSQL version

Find the line listen_addresses = 'localhost' and change it to:

listen_addresses = '100.100.100.100'  # Replace with your server's IP or '*' for all interfaces

2. pg_hba.conf: Edit the pg_hba.conf file to define which hosts are allowed to connect to your PostgreSQL databases.

sudo nano /etc/postgresql/17/main/pg_hba.conf # Adjust '17' to your PostgreSQL version

Add a line like this at the end of the file to allow connections from a specific IP range (e.g., 10.10.10.0/24) using MD5 password authentication:

# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    all             all             10.10.10.198/24         md5

Replace 10.10.10.198/24 with the network range from which you want to allow connections. For a single IP, use /32 (e.g., 10.10.10.198/32). For all IPs, use 0.0.0.0/0 (use with caution in production environments).
Restart PostgreSQL: After modifying the configuration files, restart the PostgreSQL service for the changes to take effect:

sudo systemctl restart postgresql

5. Python Migration Script
This Python script connects to a MySQL database, fetches all tables and their data, and then creates corresponding tables and inserts the data into a PostgreSQL database. It includes basic data type mapping and handles potential errors like duplicate tables or unique violations.

import pymysql
import psycopg2
import psycopg2.errors

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
mysql_conn = None
psql_conn = None
try:
# Connect to MySQL
print(f"Connecting to MySQL: {mysql_config['user']}@{mysql_config['host']}/{mysql_config['database']}")
mysql_conn = pymysql.connect(**mysql_config)
mysql_cursor = mysql_conn.cursor()
print("Successfully connected to MySQL.")

# Connect to PostgreSQL
print(f"Connecting to PostgreSQL: {psql_config['user']}@{psql_config['host']}/{psql_config['database']}")
psql_conn = psycopg2.connect(**psql_config)
psql_cursor = psql_conn.cursor()
print("Successfully connected to PostgreSQL.")

# Get list of tables from MySQL
mysql_cursor.execute("SHOW TABLES")
mysql_tables = [table[0] for table in mysql_cursor.fetchall()]
print(f"Found {len(mysql_tables)} tables in MySQL: {', '.join(mysql_tables)}")

for mysql_table in mysql_tables:
psql_table = table_mapping.get(mysql_table, mysql_table) if table_mapping else mysql_table
print(f"\nProcessing table: {mysql_table} -> {psql_table}")

# Get column information from MySQL
mysql_cursor.execute(f"DESCRIBE `{mysql_table}`") # Use backticks for MySQL table names
mysql_columns = mysql_cursor.fetchall()
psql_columns_definitions = []
column_names = []

for col in mysql_columns:
col_name = col[0]
col_type = col[1].upper()
column_names.append(col_name) # Store column names for INSERT statement

# Basic datatype mapping, add more mapping as needed.
# This mapping is simplified; for complex migrations,
# a more robust type conversion logic is required.
if "INT" in col_type:
psql_type = "INTEGER"
elif "VARCHAR" in col_type:
# Extract length from VARCHAR(N)
try:
length = col_type.split('(')[1].split(')')[0]
psql_type = f"VARCHAR({length})"
except IndexError:
psql_type = "VARCHAR(255)" # Default if length not found
elif "TEXT" in col_type:
psql_type = "TEXT"
elif "DATE" in col_type:
psql_type = "DATE"
elif "DATETIME" in col_type or "TIMESTAMP" in col_type:
psql_type = "TIMESTAMP"
elif "DECIMAL" in col_type or "NUMERIC" in col_type:
psql_type = "NUMERIC" # PostgreSQL prefers NUMERIC for exact decimals
elif "FLOAT" in col_type or "DOUBLE" in col_type:
psql_type = "DOUBLE PRECISION"
elif "BOOLEAN" in col_type or "TINYINT(1)" in col_type: # MySQL TINYINT(1) often maps to boolean
psql_type = "BOOLEAN"
else:
psql_type = "TEXT" # Default to text for unmapped types

psql_columns_definitions.append(f'"{col_name}" {psql_type}') # Quote column names for PostgreSQL

# Create table in PostgreSQL
create_table_sql = f"CREATE TABLE IF NOT EXISTS \"{psql_table}\" ({', '.join(psql_columns_definitions)})"
print(f"Creating table in PostgreSQL: {create_table_sql}")
try:
psql_cursor.execute(create_table_sql)
psql_conn.commit()
print(f"Table '{psql_table}' created or already exists.")
except Exception as e:
print(f"Error creating table {psql_table}: {e}")
psql_conn.rollback()
continue # Skip to next table if table creation fails

# Fetch data from MySQL
print(f"Fetching data from MySQL table: {mysql_table}")
mysql_cursor.execute(f"SELECT * FROM `{mysql_table}`")
rows = mysql_cursor.fetchall()
print(f"Fetched {len(rows)} rows from '{mysql_table}'.")

if not rows:
print(f"No data to migrate for table '{mysql_table}'.")
continue

# Prepare INSERT statement for PostgreSQL
# Using ON CONFLICT DO NOTHING for simple skipping of duplicates based on primary key
# For more complex conflict resolution (e.g., UPDATE), more logic is needed.
column_names_quoted = ', '.join([f'"{name}"' for name in column_names])
placeholders = ", ".join(["%s"] * len(column_names))
insert_sql = f"INSERT INTO \"{psql_table}\" ({column_names_quoted}) VALUES ({placeholders})"
print(f"Prepared INSERT statement: {insert_sql}")

# Insert data into PostgreSQL
for i, row in enumerate(rows):
try:
psql_cursor.execute(insert_sql, row)
if (i + 1) % 1000 == 0: # Commit every 1000 rows to reduce transaction size
psql_conn.commit()
print(f"Committed {i+1} rows for table '{psql_table}'.")
except psycopg2.errors.UniqueViolation:
print(f"Unique violation on table '{psql_table}', row: {row}. Skipping this row.")
psql_conn.rollback() # Rollback the current transaction on unique violation
except Exception as e:
print(f"Error inserting row: {row}, Error: {e}. Rolling back transaction for this row.")
psql_conn.rollback() # Rollback on other errors
psql_conn.commit() # Commit any remaining rows
print(f"Finished migrating data for table '{psql_table}'.")

print("\nMigration completed successfully.")

except pymysql.Error as err:
print(f"MySQL error: {err}")
except psycopg2.Error as err:
print(f"PostgreSQL error: {err}")
except Exception as err:
print(f"General Error: {err}")
finally:
if mysql_conn and mysql_conn.open:
mysql_cursor.close()
mysql_conn.close()
print("MySQL connection closed.")
if psql_conn and not psql_conn.closed: # Check if connection is not closed
psql_cursor.close()
psql_conn.close()
print("PostgreSQL connection closed.")

# Example usage:
# IMPORTANT: Replace these with your actual database credentials and hostnames/IPs.
mysql_config = {
"host": "localhost",
"user": "SQL_User", # MySQL user created earlier
"password": "Pass@123", # MySQL user password
"database": "oggy" # MySQL database to migrate from
}

psql_config = {
"host": "100.100.100.100", # PostgreSQL server IP or hostname (e.g., 'localhost' or 'your_server_ip')
"user": "PSQL_User", # PostgreSQL user created earlier
"password": "Pass@123", # PostgreSQL user password
"database": "jack" # PostgreSQL database to migrate to
}

# Optional: Define a mapping if you want PostgreSQL tables to have different names than MySQL tables.
# If a table is not in the mapping, it will be migrated with its original name.
table_mapping = {
# "mysql_table_name_1": "psql_table_name_1",
# "mysql_table_name_2": "psql_table_name_2"
}

if __name__ == "__main__":
migrate_mysql_to_psql(mysql_config, psql_config, table_mapping)


