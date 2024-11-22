import subprocess
import os
import random
import string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text


# Path to save configuration files
path = '/usr/share/blackarmy-framework/config'
# Check if the path exists, if not, create it
if not os.path.exists(path):
    try:
        os.makedirs(path, exist_ok=True)  # This will create the directory and all parent directories if they don't exist
        print(f"Path '{path}' created successfully.")
    except PermissionError:
        print(f"Permission denied. Please run the script as root to create the directory at '{path}'.")
    except Exception as e:
        print(f"Error creating path '{path}': {e}")
else:
    print(f"Path '{path}' already exists.")

# Function to generate a random password
def generate_random_password(length=12):
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
        return engine, session

    except subprocess.CalledProcessError as e:
        if verbose:
            print(f"Error during setup: {e.stderr}")
        raise
    except Exception as e:
        if verbose:
            print(f"Error: {e}")
        raise

# Example of creating a table dynamically
def create_table(engine, table_name, columns):
    try:
        with engine.connect() as conn:
            column_definitions = ", ".join([f"{name} {definition}" for name, definition in columns.items()])
            sql = text(f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions});")  # Use text para comandos brutos
            conn.execute(sql)
        print(f"Table '{table_name}' created successfully.")
    except Exception as e:
        print(f"Error creating table '{table_name}': {e}")


# When executed directly
if __name__ == "__main__":
    NEW_USER = 'blackarmy'
    NEW_DB = 'blackarmydb'

    engine, session = setup_database(
        new_user=NEW_USER,
        new_db=NEW_DB,
        verbose=True
    )

    # Example: Create a default table
    table_name = "example_table"
    columns = {
        "id": "SERIAL PRIMARY KEY",
        "name": "VARCHAR(255) NOT NULL",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    }
    create_table(engine, table_name, columns)
