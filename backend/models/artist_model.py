import os
import logging
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path

# Define paths

base_path = Path(__file__).resolve().parent.parent.parent
env_path = base_path / 'env_files' / 'special_detail.env'
log_dir = base_path / 'logger'
log_file =  log_dir / 'app.log'

# Setup a logger

logging.basicConfig(
    level=logging.DEBUG,  # Set the log level to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
    handlers=[
        logging.FileHandler(log_file),  # Log to a file named app.log in the logs directory
        logging.StreamHandler()  # Also log to the console
    ]
)

logger = logging.getLogger(__name__)

# Connect to the env file and get system variables
logger.debug(f"Loading .env file from: {env_path}")
load_dotenv(dotenv_path=env_path)

class Artists_model:

    def __init__(self, db_config: dict):
        """_
        Initialize databse connection.

        Args:
            db_config (dict): Dictionary containing database information
        """

        try:
            self.conn = mysql.connector.connect(**db_config)
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to the database: {err}")
            raise
    
    def add_new_artist(self):
        pass

    def fetch_songs_from_artist(self):
        pass

    def fetch_albums_from_artist(self):
        pass

    def update_artist_infromation(self):
        pass

    def delete_artist(self):
        pass

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}
