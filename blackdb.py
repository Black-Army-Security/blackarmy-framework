import subprocess
import os
import sys
import random
import string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

# Path to save configuration files
config_path = '/usr/share/blackarmy-framework/config'
database_config_file = os.path.join(config_path, 'database.yml')

if os.geteuid() != 0:
    print("""
[ERROR] Permission Denied!
This script requires administrative privileges to run.

Please re-run the script using sudo:
    sudo python3 blackdb.py

If you believe this is an error, ensure you have the correct permissions.
""")
    sys.exit(1)


# Check if the path exists, if not, create it
if not os.path.exists(config_path):
    try:
        os.makedirs(config_path, exist_ok=True)  # This will create the directory and all parent directories if they don't exist
        print(f"Path '{config_path}' created successfully.")
    except PermissionError:
        print(f"Permission denied. Please run the script as root to create the directory at '{config_path}'.")
    except Exception as e:
        print(f"Error creating path '{config_path}': {e}")
else:
    print(f"Path '{config_path}' already exists.")

# Function to generate a random password
def generate_random_password(length=24):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

# Unified function to handle database setup and initialization using subprocess
def setup_database(new_user, new_db, verbose=False):
    try:
        # Generate a random password for the user
        new_password = generate_random_password()
        if verbose:
            print(f"Generated password for user '{new_user}': {new_password}")

        # SQL commands to create user and database
        create_user_sql = f"CREATE ROLE {new_user} WITH LOGIN PASSWORD '{new_password}';"
        create_db_sql = f"CREATE DATABASE {new_db} OWNER {new_user};"

        # Execute the commands as the 'postgres' user
        subprocess.run(['sudo', '-u', 'postgres', 'psql', '-c', create_user_sql], check=True)
        if verbose:
            print(f"User '{new_user}' created successfully.")

        subprocess.run(['sudo', '-u', 'postgres', 'psql', '-c', create_db_sql], check=True)
        if verbose:
            print(f"Database '{new_db}' created successfully.")

        # Initialize the database connection
        db_uri = f'postgresql://{new_user}:{new_password}@localhost/{new_db}'
        engine = create_engine(db_uri)
        Session = sessionmaker(bind=engine)
        session = Session()
        if verbose:
            print("Database initialized successfully.")
        return engine, session, new_password

    except subprocess.CalledProcessError as e:
        if verbose:
            print(f"Error during setup: {e.stderr}")
        raise
    except Exception as e:
        if verbose:
            print(f"Error: {e}")
        raise

# Save database configurations to YAML
def save_to_yaml(file_path, configs):
    try:
        with open(file_path, 'w') as file:
            file.write(configs)
        print(f"Database configurations saved to '{file_path}'.")
    except Exception as e:
        print(f"Error saving configurations to '{file_path}': {e}")

# Example of creating a table dynamically
def create_table(engine, table_name, columns):
    try:
        with engine.connect() as conn:
            column_definitions = ", ".join([f"{name} {definition}" for name, definition in columns.items()])
            sql = text(f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions});")
            conn.execute(sql)
        print(f"Table '{table_name}' created successfully.")
    except Exception as e:
        print(f"Error creating table '{table_name}': {e}")

# When executed directly
if __name__ == "__main__":
    # Setup for the first user and database
    USER1 = 'blackarmy'
    DB1 = 'blackarmydb'

    engine1, session1, password1 = setup_database(
        new_user=USER1,
        new_db=DB1,
        verbose=True
    )
    print(f"User: {USER1}, Password: {password1}")

    # Setup for the second user and database
    USER2 = 'blackarmy_test'
    DB2 = 'blackarmydb_test'

    engine2, session2, password2 = setup_database(
        new_user=USER2,
        new_db=DB2,
        verbose=True
    )
    print(f"User: {USER2}, Password: {password2}")

    # Save configurations to YAML file
    yaml_config = f"""
production:
  adapter: postgresql
  database: {DB1}
  username: {USER1}
  password: {password1}
  host: localhost
  port: 5432
  pool: 5
  timeout: 5

test:
  adapter: postgresql
  database: {DB2}
  username: {USER2}
  password: {password2}
  host: localhost
  port: 5432
  pool: 5
  timeout: 5
"""
    save_to_yaml(database_config_file, yaml_config)

    # Example: Create a default table in each database
    table_name = "example_table"
    columns = {
        "id": "SERIAL PRIMARY KEY",
        "name": "VARCHAR(255) NOT NULL",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }
    
    create_table(engine1, table_name, columns)
    create_table(engine2, table_name, columns)
