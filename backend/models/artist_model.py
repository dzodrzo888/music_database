import os
import logging
import mysql.connector
from dotenv import load_dotenv
from pathlib import Path
import sys

base_path = Path(__file__).resolve().parent.parent.parent
env_path = base_path / 'env_files' / 'special_detail.env'
log_dir = base_path / 'logger'
log_file =  log_dir / 'app.log'

sys.path.append(str(base_path))

from utils.errors import InputError
from utils.errors import DatabaseConnectionError
from backend.database_manager.database_manager import DatabaseManager

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
logger.info(f"Loading .env file from: {env_path}")
load_dotenv(dotenv_path=env_path)

class Artists_model:

    def __init__(self, cursor):
        """
        Initialize the UserModel class with database configuration.

        Args:
            cursor (mysql.connector.cursor_cext.CMySQLCursorDict): The database cursor.

        Raises:
                DatabaseConnectionError: If connection to the database fails
        """
        try:
            self.cursor = cursor
            self.cursor.execute("SHOW COLUMNS FROM Artists;")
            self.table_columns = self.cursor.fetchall()
            logger.info("Database connection established successfully.")
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to the database: {err}")
            raise DatabaseConnectionError(f"Error connecting to the database: {err}")

    def string_checker(self, string: str):
        """
        Function to check if a input is a string

        Args:
            string (str): Any string to be checked.
                        Example: "a"

        Raises:
            ValueError: If input is not a string.
                        If string is with whitespaces.
        Returns:
            string_stripped (str): Returns a string striped
                        Example: "a"            
        """


        if not isinstance(string, str):
            logger.error("Input is not a string!")
            raise ValueError("Input must be a non-empty string.")

        if not string.strip():
            logger.info("Input must be a non empty string")
            raise ValueError("Input must be a non empty string")
        
        string_stripped = string.strip()

        return string_stripped

    def check_if_input_cols_match(self, table_columns: list, input_columns: list, exclude_columns = None, exact_match=True):
        """
        Checks if columns that want to be inputed match the table columns raises a InputError if not.

        Args:
            table_columns (list): List of columns from a sql table,
            input_columns (list): List of columns that want to be inputed.

        Raises:
            InputError: If the columns dont match and we need a exact match.
                        If the column does not match any other columns from the table.
        """

        if not exclude_columns:
            exclude_columns = []

        table_columns_filtered = [col for col in table_columns if col not in exclude_columns]

        if set(input_columns) != set(table_columns_filtered) and exact_match:
            logger.error("Inputed columns dont match the table columns")
            raise InputError("Inputed columns dont match the table columns")
        
        if not exact_match and not set([input_columns]).issubset(set(table_columns_filtered)):
            logger.error("Inputed columns that are not in the table schema!")
            raise InputError("Inputed columns that are not in the table schema!") 
    
    def add_new_artist(self, artist_info: dict):
        """
        Inserts a artist into the Artists database.

        Args:
            user_data (dict): A dictionary containing details about the artist.
        Raises:
            InputError: If the set of columns does not equal the columns from the table.
            DatabaseConnectionError: If the database connection fails.
        """
        try:
            columns_table = [row["Field"] for row in self.table_columns]
            columns_dict = [col for col in artist_info.keys()]
            excluded_cols = ["id", "deleted"]

            # Check if the table columns match the input columns
            self.check_if_input_cols_match(table_columns=columns_table, input_columns=columns_dict, exclude_columns=excluded_cols)

            input_columns_string = ", ".join(artist_info.keys())
            placeholders = ", ".join(["%s"] * len(artist_info))

            query = f"""
                        INSERT INTO `Artists`({input_columns_string}) 
                        VALUES({placeholders});
                    """
            artist_info_tuple = tuple(artist_info.values())
            self.cursor.execute(query, artist_info_tuple)
            logger.info(f"New artist added {artist_info["name"]}")
        except mysql.connector.Error as err:
            logger.error(f"Error when createing a new artist {err}")
            raise DatabaseConnectionError(f"Database connection failed {err}.")

    def fetch_songs_from_artist(self, artist_name: str) -> dict:
        """
        Fetch songs from a specific artist.

        Args:
            artist_name (str): Artists_name.

        Returns:
            artists_songs (dict): dict containing the name of the artists and all their songs (list).
        
        Raises: 
            DatabaseConnectionError: If connection to the database fails
        """

        try:
            artist_name = self.string_checker(artist_name)
            
            query = """
                    SELECT a.name AS artist_name, s.name AS song_name FROM non_deleted_artists AS a
                    JOIN Songs AS s ON a.id = s.artist_id
                    WHERE a.name = %s
                    """
            self.cursor.execute(query, (artist_name, ))
            artists_songs_fetched = self.cursor.fetchall()
            
            if not artists_songs_fetched:
                logger.warning("No artists feteched")
                return {}
            
            artists_songs = {artist_name: [i["song_name"] for i in artists_songs_fetched]}
            logger.info(f"Songs from {artist_name} fetched")
            return artists_songs
        except mysql.connector.Error as err:
            logger.error(f"Error fetching songs {err}")
            raise DatabaseConnectionError(f"Error fetching songs {err}")

    def fetch_albums_from_artist(self, artist_name: str) -> dict:
        """
        Fetches albums from a artist.

        Args:
            artist_name (str): Artist name.

        Returns:
            artists_albums (dict): dict containing the name of the artists and all their albums (list).
        
        Raises: 
            DatabaseConnectionError: If connection to the database fails.

        """

        try:
            artist_name = self.string_checker(artist_name)
            query = """
                    SELECT ar.name AS artist_name, al.name AS album_name FROM non_deleted_artists AS ar
                    JOIN Albums AS al ON ar.id = al.artist_id
                    WHERE ar.name = %s
                    """
            self.cursor.execute(query, (artist_name, ))
            artists_albums_fetched = self.cursor.fetchall()
            
            if not artists_albums_fetched:
                logger.info("No albums feteched")
                return {}
            
            artists_albums = {artist_name: [i["album_name"] for i in artists_albums_fetched]}
            logger.info(f"Albums from {artist_name} fetched")
            return artists_albums
        except mysql.connector.Error as err:
            logger.error(f"Error fetching the albums {err}")
            raise DatabaseConnectionError(f"Error fetching the albums {err}")

    def update_artist_infromation(self, artist_update_info: dict, artist_name: str):
        """
        Function to update artists info.

        Args:
            artist_update_info (dict): dict containing the column and the value that will be changed for a artist.
            artist_name (str): Artists name.
        
        Raises:
                InputError: If len of artist_update info not 1.
                            if column is not in the artists table
                DatabaseConnectionError: If connection to the database fails
        """
        try:
            column_table = [row["Field"] for row in self.table_columns]

            column_dict, value = next(iter(artist_update_info.items()))

            # Check if input is a string
            artist_name = self.string_checker(artist_name)
            
            if  len(artist_update_info) != 1:
                logger.error("Dictionary doesnt have just one key-value pair")
                raise InputError("Dictionary doesnt have just one key-value pair")

            self.check_if_input_cols_match(table_columns=column_table, input_columns=column_dict, exact_match=False)
            
            query = f"""
                    UPDATE Artists
                    SET {column_dict} = %s
                    WHERE name = %s
                    """
            self.cursor.execute(query, (value, artist_name))
            logger.info(f"{artist_name} info updated on {column_dict} to {value}")
        except mysql.connector.Error as err:
            logger.error(f"Error updating a artist info {err}")
            raise DatabaseConnectionError(f"Error updating a artist info {err}")

    def soft_delete_artist(self, artist_name: str):
        """
        This function takes a artist name as input and marks him as deleted in our database.

        Args:
            artist_name (string): Name of a artists.
                Example: "Billy Joel"

        Raises:
            ValueError: If artist_name is not a string.
            DatabaseConnectionError: If database error occurs during the database creation.
        """
        try:
            artist_name = self.string_checker(artist_name)
            query = """
                    UPDATE Artists
                    SET deleted = 1
                    WHERE name = %s
                    """
            self.cursor.execute(query, (artist_name, ))
            logger.info(f"{artist_name} deleted")
        except mysql.connector.Error as err:
            logger.error(f"Error deleting a artist {err}")
            raise DatabaseConnectionError(f"Error deleting a artist {err}")

    def fetch_all_artists(self):
        """
        Fetches all artists from the database.

        Args:
            None
        Returns:
            all_artists (list): Return all the non deleted artists from the database.
        Raises:
            DatabaseConnectionError: If database error occurs during the database creation
        """
        try:
            query = """
                    SELECT name FROM non_deleted_artists
                    """
            self.cursor.execute(query)
            all_artists_fetched = self.cursor.fetchall()

            if not all_artists_fetched:
                logger.warning("No Artists found")
                return []

            all_artists = [row['name'] for row in all_artists_fetched]
            logger.info("All artists fetched")
            return all_artists
        
        except mysql.connector.Error as err:
            logger.error(f"Databse connection failed {err}")
            raise DatabaseConnectionError(f"Databse connection failed {err}")

    def close_connection(self):
        self.cursor.close()
        self.conn.close()
        logger.info("Database connection closed.")

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

artist = {
    "name": "Suki Waterhouse",
    "genre": "Pop",
    "profile_image": None
}
