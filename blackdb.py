import psycopg2
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Initialize SQLAlchemy interpreter
Base = declarative_base()

#vvv Table model
class Data(Base):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    value = Column(Float, nullable=False)
#^^^^

# Create database and user
def create_db(admin_db_uri, new_user, new_password, new_db, verbose=False):
    try:
        conn = psycopg2.connect(admin_db_uri)
        conn.autocommit = True
        cur = conn.cursor()

        # Create user
        cur.execute(f"""
            DO $$ BEGIN
                CREATE ROLE {new_user} WITH LOGIN PASSWORD '{new_password}';
            EXCEPTION WHEN OTHERS THEN NULL;
            END $$;
        """)
        if verbose:
            print(f"User '{new_user}' verified/created.")

        # Create database
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
    except Exception as e:
        if verbose:
            print("Error creating user or database:", e)

# Initialize database and create tables defined by the model
def initialize_db(uri, verbose=False):
    try:
        engine = create_engine(uri)
        Base.metadata.create_all(engine)  
        if verbose:
            print("Tables successfully created/verified.")
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        if verbose:
            print("Error initializing the database:", e)
        raise

'''
# Example usage
if __name__ == "__main__":
    # Superuser and database configuration
    ADMIN_URI = 'postgresql://admin:admin_pass@localhost/postgres'
    NEW_USER = 'my_user'
    NEW_PASSWORD = 'my_password'
    NEW_DB = 'my_database'

    # Create the database and user
    create_db(
        admin_db_uri=ADMIN_URI,
        new_user=NEW_USER,
        new_password=NEW_PASSWORD,
        new_db=NEW_DB,
        verbose=True
    )

    # Initialize the database
    DB_URI = f'postgresql://{NEW_USER}:{NEW_PASSWORD}@localhost/{NEW_DB}'
    session = initialize_db(DB_URI, verbose=True)

    # Example operation (optional)
    new_entry = Data(name="Example", value=123.45)
    session.add(new_entry)
    session.commit()
    print("Entry successfully added to the database.")
'''
