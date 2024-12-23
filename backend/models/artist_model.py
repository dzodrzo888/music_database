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
    
    def add_new_artist(self, artist_info: dict):
        try:
            query = """
                    INSERT INTO `Artists`(name, genre, profile_image)
                    VALUES(%s, %s, %s)
                    """
            artist_info_tuple = tuple(artist_info.values())
            self.cursor.execute(query, artist_info_tuple)
            self.conn.commit()
            logger.info(f"New artist added {artist_info["name"]}")
        except mysql.connector.Error as err:
            logger.error(f"Error when createing a new artist {err}")
            raise

    def fetch_songs_from_artist(self, artist_name: str) -> dict:
        """
        Fetch songs from a specific artist.

        Args:
            artist_name (str): Artists_name.

        Returns:
            artists_songs (dict): dict containing the name of the artists and all their songs (list).
        """

        try:
            query = """
                    SELECT a.name, s.name FROM Artists AS a
                    JOIN Songs AS s ON a.id = s.artist_id
                    WHERE a.name = %s
                    """
            self.cursor.execute(query, (artist_name, ))
            artists_songs_fetched = self.cursor.fetchall()
            
            if not artists_songs_fetched:
                logger.info("No artists feteched")
                return {}
            
            artists_songs = {artists_songs_fetched[0][0]: [i[1] for i in artists_songs_fetched]}
            logger.info(f"Songs from {artist_name} fetched")
            return artists_songs
        except mysql.connector.Error as err:
            logger.error(f"Error fetching songs {err}")
            raise

    def fetch_albums_from_artist(self, artist_name: str) -> dict:
        """
        Fetches albums from a artist.

        Args:
            artist_name (str): Artist name.

        Returns:
            artists_albums (dict): dict containing the name of the artists and all their albums (list).
        """

        try:
            query = """
                    SELECT ar.name, al.name FROM Artists AS ar
                    JOIN Albums AS al ON ar.id = al.artist_id
                    WHERE ar.name = %s
                    """
            self.cursor.execute(query, (artist_name, ))
            artists_albums_fetched = self.cursor.fetchall()
            
            if not artists_albums_fetched:
                logger.info("No albums feteched")
                return {}
            
            artists_albums = {artists_albums_fetched[0][0]: [i[1] for i in artists_albums_fetched]}
            logger.info(f"Albums from {artist_name} fetched")
            return artists_albums
        except mysql.connector.Error as err:
            logger.error(f"Error fetching the albums {err}")
            raise

    def update_artist_infromation(self, artist_update_info: dict, artist_name: str):
        """
        Function to update artists info.

        Args:
            artist_update_info (dict): dict containing the column and the value that will be changed for a artist.
            artist_name (str): Artists name.
        """
        try:
            column, value = next(iter(artist_update_info.items()))

            ALLOWED_COLUMNS = {"name", "genre", "profile_image"}

            if column not in ALLOWED_COLUMNS:
                logger.error(f"Invalid column: {column}")
                raise ValueError(f"Invalid column: {column}")
            
            query = f"""
                    UPDATE Artists
                    SET {column} = %s
                    WHERE name = %s
                    """
            self.cursor.execute(query, (value, artist_name))
            self.conn.commit()
            logger.info(f"{artist_name} info updated on {column} to {value}")
        except mysql.connector.Error as err:
            logger.error(f"Error updating a artist info {err}")
            raise

    def delete_artist(self, artist_name: str):
        try:
            query = """
                    UPDATE Artists
                    SET deleted = 1
                    WHERE name = %s
                    """
            self.cursor.execute(query, (artist_name, ))
            self.conn.commit()
            logger.info(f"{artist_name} deleted")
        except mysql.connector.Error as err:
            logger.error(f"Error deleting a artist {err}")
            raise

    def fetch_all_artists(self):
        """
        Fetches all artists from the database.

        Args:
            ...
        Returns:
            all_artists (list): Return all the non deleted artists from the database.
        """
        try:
            query = """
                    SELECT * FROM non_deleted_artists
                    """
            self.cursor.execute(query)
            all_artists_fetched = self.cursor.fetchall()
            all_artists = [i[1] for i in all_artists_fetched]
            logger.info("All artists fetched")
            return all_artists
        except mysql.connector.Error as err:
            logger.error(f"Error fetching all artis {err}")
            raise

    def close_connection(self):
        self.cursor.close()
        self.conn.close()
        logger.info("Database connection closed.")

#db_config = {
 #   'host': os.getenv('DB_HOST'),
  #  'user': os.getenv('DB_USER'),
   # 'password': os.getenv('DB_PASSWORD'),
    #'database': os.getenv('DB_NAME')
#}
