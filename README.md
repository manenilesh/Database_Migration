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

