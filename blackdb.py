from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import psycopg2
import random
import string

# Function to generate a random password
def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

# Unified function to handle database setup and initialization
def setup_database(admin_db_uri, new_user, new_db, verbose=False):
    try:
        # Generate a random password for the user
        new_password = generate_random_password()
        if verbose:
            print(f"Generated password for user '{new_user}': {new_password}")

        # Create the database and user
        conn = psycopg2.connect(admin_db_uri)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(f"""
            DO $$ BEGIN
                CREATE ROLE {new_user} WITH LOGIN PASSWORD '{new_password}';
            EXCEPTION WHEN OTHERS THEN NULL;
            END $$;
        """)
        if verbose:
            print(f"User '{new_user}' verified/created.")

        cur.execute(f"""
            DO $$ BEGIN
                CREATE DATABASE {new_db} OWNER {new_user};
            EXCEPTION WHEN OTHERS THEN NULL;
            END $$;
        """)
        if verbose:
            print(f"Database '{new_db}' verified/created.")

        cur.close()
        conn.close()

        # Initialize the database connection
        db_uri = f'postgresql://{new_user}:{new_password}@localhost/{new_db}'
        engine = create_engine(db_uri)
        Session = sessionmaker(bind=engine)
        session = Session()
        if verbose:
            print("Database initialized successfully.")
        return engine, session

    except Exception as e:
        if verbose:
            print(f"Error during setup: {e}")
        raise

# Example of creating a table dynamically
def create_table(engine, table_name, columns):
    try:
        with engine.connect() as conn:
            column_definitions = ", ".join([f"{name} {definition}" for name, definition in columns.items()])
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions});"
            conn.execute(sql)
        print(f"Table '{table_name}' created successfully.")
    except Exception as e:
        print(f"Error creating table '{table_name}': {e}")

# When executed directly
if __name__ == "__main__":
    ADMIN_URI = 'postgresql://postgres@localhost/postgres'
    NEW_USER = 'blackarmy'
    NEW_DB = 'blackarmydb'

    engine, session = setup_database(
        admin_db_uri=ADMIN_URI,
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
