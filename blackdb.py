import subprocess
import os
import sys
import random
import string
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import text

# Path to save configuration files
config_path = '/usr/share/blackarmy-framework/config'
database_config_file = os.path.join(config_path, 'database.yml')

Base = declarative_base()

if os.geteuid() != 0:
    print("""
[ERROR] Permission Denied!
This script requires administrative privileges to run.

Please re-run the script using sudo:
    sudo python3 blackdb.py

If you believe this is an error, ensure you have the correct permissions.
""")
    sys.exit(1)

# Check if the path exists
if os.path.exists(config_path):
    print(f"Path '{config_path}' already exists.")
else:
    try:
        os.makedirs(config_path, exist_ok=True)
        print(f"Path '{config_path}' created successfully.")
    except PermissionError:
        print(f"Permission denied. Please run the script as root to create the directory at '{config_path}'.")
    except Exception as e:
        print(f"Error creating path '{config_path}': {e}")


# Function to generate a random password
def generate_random_password(length=24):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

# Unified function to handle database setup and initialization
def setup_database(new_user, new_db, verbose=False):
    try:
        new_password = generate_random_password()
        if verbose:
            print(f"Generated password for user '{new_user}': {new_password}")

        # SQL commands to create user and database
        create_user_sql = f"CREATE ROLE {new_user} WITH LOGIN PASSWORD '{new_password}';"
        create_db_sql = f"CREATE DATABASE {new_db} OWNER {new_user};"

        # Suppress output of the subprocess commands
        subprocess.run(['sudo', '-u', 'postgres', 'psql', '-c', create_user_sql], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['sudo', '-u', 'postgres', 'psql', '-c', create_db_sql], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Initialize the database connection
        db_uri = f'postgresql://{new_user}:{new_password}@localhost/{new_db}'
        engine = create_engine(db_uri)
        Session = sessionmaker(bind=engine)
        session = Session()
        if verbose:
            print(f"Database '{new_db}' initialized successfully.")
        return engine, session, new_password
    except subprocess.CalledProcessError as e:
        print(f"Error during setup: {e.stderr}")
        raise
    except Exception as e:
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

# Define the tables
class Target(Base):
    __tablename__ = 'targets'
    id = Column(Integer, primary_key=True)
    domain = Column(String(255), nullable=False)
    ip = Column(String(255))
    os = Column(String(255))
    waf = Column(String(255))

class Subdomain(Base):
    __tablename__ = 'subdomains'
    id = Column(Integer, primary_key=True)
    target_id = Column(Integer, ForeignKey('targets.id'))
    subdomain = Column(String(255), nullable=False)
    ip = Column(String(255))
    target = relationship('Target', back_populates='subdomains')

Target.subdomains = relationship('Subdomain', order_by=Subdomain.id, back_populates='target')

class Port(Base):
    __tablename__ = 'ports'
    id = Column(Integer, primary_key=True)
    subdomain_id = Column(Integer, ForeignKey('subdomains.id'))
    port = Column(Integer, nullable=False)
    protocol = Column(String(10), nullable=False)
    state = Column(String(10), nullable=False)
    subdomain = relationship('Subdomain', back_populates='ports')

Subdomain.ports = relationship('Port', order_by=Port.id, back_populates='subdomain')

class Service(Base):
    __tablename__ = 'services'
    id = Column(Integer, primary_key=True)
    port_id = Column(Integer, ForeignKey('ports.id'))
    service_name = Column(String(255), nullable=False)
    version = Column(String(255))
    port = relationship('Port', back_populates='services')

Port.services = relationship('Service', order_by=Service.id, back_populates='port')

class Vulnerability(Base):
    __tablename__ = 'vulnerabilities'
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('services.id'))
    vulnerability = Column(Text, nullable=False)
    severity = Column(String(50))
    cve_id = Column(String(50))
    service = relationship('Service', back_populates='vulnerabilities')

Service.vulnerabilities = relationship('Vulnerability', order_by=Vulnerability.id, back_populates='service')

# Create the tables in the database
def create_tables(engine):
    try:
        Base.metadata.create_all(engine)
        print("All tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

# When executed directly
if __name__ == "__main__":
    databases = [
        ('blackarmy', 'blackarmydb'),
        ('blackarmy_test', 'blackarmydb_test')
    ]

    yaml_configs = []

    for user, db in databases:
        engine, session, password = setup_database(
            new_user=user,
            new_db=db,
            verbose=True
        )
        create_tables(engine)
        yaml_configs.append(f"""
{user}:
  adapter: postgresql
  database: {db}
  username: {user}
  password: {password}
  host: localhost
  port: 5432
  pool: 5
  timeout: 5
""")

    # Save all database configurations to YAML
    save_to_yaml(database_config_file, "\n".join(yaml_configs))