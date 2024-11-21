import psycopg2
import os
import random
import string
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


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


# Initialize SQLAlchemy interpreter
Base = declarative_base()

# Table model definition
class Data(Base):
    __tablename__ = 'blackarmydb'  # The table name is 'blackarmydb'
    id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key, auto-incremented
    name = Column(String, nullable=False)  # 'name' field cannot be null
    value = Column(Float, nullable=False)  # 'value' field cannot be null


# Function to create a random password
def generate_random_password(length=12):
    """Generates a random password with letters and digits."""
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for i in range(length))
    return password


# Function to create the database and user
def create_db(admin_db_uri, new_user, new_password, new_db, verbose=False):
    try:
        # Connect to the PostgreSQL database as an administrator using the provided URI
        conn = psycopg2.connect(admin_db_uri)
        conn.autocommit = True  # Enable autocommit to immediately apply commands
        cur = conn.cursor()

        # Create the new user (if it doesn't exist)
        cur.execute(f"""
            DO $$ BEGIN
                CREATE ROLE {new_user} WITH LOGIN PASSWORD '{new_password}';
            EXCEPTION WHEN OTHERS THEN NULL;
            END $$;
        """)
        if verbose:
            print(f"User '{new_user}' verified/created.")

        # Create the new database (if it doesn't exist)
        cur.execute(f"""
            DO $$ BEGIN
                CREATE DATABASE {new_db} OWNER {new_user};
            EXCEPTION WHEN OTHERS THEN NULL;
            END $$;
        """)
        if verbose:
            print(f"Database '{new_db}' verified/created.")

        # Close the cursor and connection
        cur.close()
        conn.close()
    except Exception as e:
        # If an error occurs, print the exception message
        if verbose:
            print("Error creating user or database:", e)


# Function to initialize the database and create tables defined by the model
def initialize_db(uri, verbose=False):
    try:
        # Connect to the database using SQLAlchemy's engine
        engine = create_engine(uri)
        # Create all tables defined in the model (e.g., 'Data' table)
        Base.metadata.create_all(engine)
        if verbose:
            print("Tables successfully created/verified.")
        
        # Create a session factory to interact with the database
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        # If an error occurs, print the exception message
        if verbose:
            print("Error initializing the database:", e)
        raise


# Example usage
if __name__ == "__main__":
    # Superuser and database configuration
    ADMIN_URI = 'postgresql://postgres@localhost/postgres'  # URI for the superuser (postgres)
    NEW_USER = 'blackarmy'  # Name of the new user to be created
    NEW_PASSWORD = generate_random_password()  # Generate a random password for the new user
    NEW_DB = 'blackarmydb'  # Name of the new database to be created

    # Print the generated password
    print(f"Generated password for user '{NEW_USER}': {NEW_PASSWORD}")

    # Create the database and user
    create_db(
        admin_db_uri=ADMIN_URI,
        new_user=NEW_USER,
        new_password=NEW_PASSWORD,
        new_db=NEW_DB,
        verbose=True
    )

    # Initialize the database connection
    DB_URI = f'postgresql://{NEW_USER}:{NEW_PASSWORD}@localhost/{NEW_DB}'  # URI for the new user and database
    session = initialize_db(DB_URI, verbose=True)

    # Example operation: add a new entry to the 'Data' table
    new_entry = Data(name="Example", value=123.45)  # Create a new Data entry
    session.add(new_entry)  # Add the entry to the session
    session.commit()  # Commit the transaction (save the entry in the database)
    print("Entry successfully added to the database.")