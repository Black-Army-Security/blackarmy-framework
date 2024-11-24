import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Path to the YAML configuration file
yaml_file_path = '/usr/share/blackarmy-framework/config/database.yml'

# Load the configurations from the YAML file
with open(yaml_file_path, 'r') as file:
    config = yaml.safe_load(file)

# Select the configuration for the 'blackarmy' environment (or another one if preferred)
db_config = config['blackarmy']

# Create the connection URL for PostgreSQL
db_url = (
    f"postgresql://{db_config['username']}:{db_config['password']}"
    f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
)

# Create the SQLAlchemy engine
engine = create_engine(db_url, echo=True)

# Create the session factory
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test the connection to the database
try:
    with engine.connect() as connection:
        result = connection.execute("SELECT 1")
        print("Connection successful:", result.fetchone())
except Exception as e:
    print("Error connecting to the database:", e)
