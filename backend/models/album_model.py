import mysql.connector
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Define paths

base_path = Path(__file__).resolve().parent.parent.parent
env_path = base_path / 'env_files' / 'special_detail.env'
log_file = base_path / 'logger' / 'app.log'

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

class Albums_models:

    def __init__(self, db_config):
        """
        Initializes Albums class, sets database and connector variables.

        Args:
            db_config (dict): Dictionary containing database info
        """
        try:
            self.conn = mysql.connector.connect(**db_config)
            self.cursor = self.conn.cursor()
            logger.info("Succesfully connected to the database")
        except mysql.connector.Error as err:
            logger.error(f"Database connection failed {err}")
            raise

    def add_new_album(self, artist_info: dict):
        try:
            query = """
                    INSERT INTO Albums(artist_id, name, release_date, album_image)
                    VALUES(%s, %s, %s, %s)
                    """
            artist_info_tuple = tuple(artist_info.items())
            self.cursor.execute(query, artist_info_tuple)
            self.conn.commit()
            logger.info(f"{artist_info["name"]} added to the database")
        except mysql.connector.Error as err:
            logger.error(f"Error adding artist to the database {err}")
            raise

    def fetch_songs_from_album(self):
        pass

    def update_album_information(self):
        pass

    def soft_delete_album(self):
        pass

    def close_connection(self):
        pass

#db_config = {
 #   'host': os.getenv('DB_HOST'),
  #  'user': os.getenv('DB_USER'),
   # 'password': os.getenv('DB_PASSWORD'),
    #'database': os.getenv('DB_NAME')
#}