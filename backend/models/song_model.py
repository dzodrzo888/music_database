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

class Song_model:

    def __init__(self, cursor):
        """
        Initialize the Song_model class with database configuration.

        Args:
            cursor (mysql.connector.cursor_cext.CMySQLCursorDict): The database cursor.

        Raises:
                DatabaseConnectionError: If connection to the database fails.
        """
        try:
            self.cursor = cursor
            self.cursor.execute("SHOW COLUMNS FROM Songs;")
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
    
    def add_new_song(self, song_info: dict):
        """
        Inserts a song into the Songs database.

        Args:
            song_info (dict): A dictionary containing details about the song.
            
        Raises:
            InputError: If the set of columns does not equal the columns from the table.
            DatabaseConnectionError: If the database connection fails.
        """
        try:
            columns_table = [row["Field"] for row in self.table_columns]
            columns_dict = [col for col in song_info.keys()]
            excluded_cols = ["id", "deleted"]

            # Check if the table columns match the input columns
            self.check_if_input_cols_match(table_columns=columns_table, input_columns=columns_dict, exclude_columns=excluded_cols)

            input_columns_string = ", ".join(song_info.keys())
            placeholders = ", ".join(["%s"] * len(song_info))

            query = f"""
                        INSERT INTO `Songs`({input_columns_string}) 
                        VALUES({placeholders});
                    """
            song_info_tuple = tuple(song_info.values())
            self.cursor.execute(query, song_info_tuple)
            logger.info(f"New song added {song_info["name"]}")
        except mysql.connector.Error as err:
            logger.error(f"Error when createing a new song {err}")
            raise DatabaseConnectionError(f"Database connection failed {err}.")

    def fetch_song_details(self, song_name:str) -> list:
        """
        Fetches details about a specific song.

        Args:
            song_name (str): Song name
        Returns:
            song_details (list): Return details about a specific song.
                Example = [{'id': 2, 'album_id': 1, 'artist_id': 1, 'name': 'Something', 'release_date': datetime.datetime(1969, 9, 26, 0, 0), 'song_image': None, 'deleted': 0}]
        Raises:
            DatabaseConnectionError: If database error occurs during the database creation
        """
        try:
            query = f"""
                    SELECT * FROM non_deleted_songs
                    WHERE name = '{song_name}';
                    """
            
            print(query)
            self.cursor.execute(query)
            song_details_fetched = self.cursor.fetchall()
            if not song_details_fetched:
                logger.warning("Song not found")
                return []

            logger.info("Song details fetched")
            return song_details_fetched
        except mysql.connector.Error as err:
            logger.error(f"Databse connection failed {err}")
            raise DatabaseConnectionError(f"Databse connection failed {err}")

    def fetch_specific_songs(self, column: str, value: str) -> list:
        """
        Fetches specific songs based on a column and a value

        Args:
            column (str): column in a table 
            value (str): value to be looked up in the table
        Returns:
            song_details (list): Return details about a specific song.
        Raises:
            DatabaseConnectionError: If database error occurs during the database creation
        """
        try:
            query = f"""
                    SELECT name FROM non_deleted_songs
                    WHERE {column} = '{value}';
                    """
            
            print(query)
            self.cursor.execute(query)
            songs_fetched = self.cursor.fetchall()
            if not songs_fetched:
                logger.warning("Song not found")
                return []
            specific_songs = [row["name"] for row in songs_fetched]
            logger.info("Specific songs fetched")
            return specific_songs
        except mysql.connector.Error as err:
            logger.error(f"Databse connection failed {err}")
            raise DatabaseConnectionError(f"Databse connection failed {err}")

    def fetch_all_songs(self) -> list:
        """
        Fetches all songs from the database.

        Args:
            None
        Returns:
            all_songs (list): Return all the non deleted songs from the database.
        Raises:
            DatabaseConnectionError: If database error occurs during the database creation
        """
        try:
            query = """
                    SELECT name FROM non_deleted_songs
                    """
            self.cursor.execute(query)
            all_songs_fetched = self.cursor.fetchall()

            if not all_songs_fetched:
                logger.warning("No Songs found")
                return []

            all_songs = [row['name'] for row in all_songs_fetched]
            logger.info("All songs fetched")
            return all_songs
        
        except mysql.connector.Error as err:
            logger.error(f"Databse connection failed {err}")
            raise DatabaseConnectionError(f"Databse connection failed {err}")

    def update_song_details(self, song_update_info: dict, song_name: str):
        """
        Function to update songs info.

        Args:
            song_update_info (dict): dict containing the column and the value that will be changed for a song.
            song_name (str): Song name.
        
        Raises:
                InputError: If len of song_update_info info not 1.
                            if column is not in the songs table
                DatabaseConnectionError: If connection to the database fails
        """
        try:
            column_table = [row["Field"] for row in self.table_columns]

            column_dict, value = next(iter(song_update_info.items()))
            # Check if input is a string
            song_name = self.string_checker(song_name)
            
            if  len(song_update_info) != 1:
                logger.error("Dictionary doesnt have just one key-value pair")
                raise InputError("Dictionary doesnt have just one key-value pair")

            self.check_if_input_cols_match(table_columns=column_table, input_columns=column_dict, exact_match=False)
            
            query = f"""
                    UPDATE Songs
                    SET {column_dict} = %s
                    WHERE name = %s
                    """
            self.cursor.execute(query, (value, song_name))
            logger.info(f"{song_name} info updated on {column_dict} to {value}")
        except mysql.connector.Error as err:
            logger.error(f"Error updating a song info {err}")
            raise DatabaseConnectionError(f"Error updating a song info {err}")

    def soft_delete_songs(self, song_name: str):
        """
        This function takes a song name as input and marks him as deleted in our database.

        Args:
            song_name (string): Name of a songs.
                Example: "Come together"

        Raises:
            ValueError: If song_name is not a string.
            DatabaseConnectionError: If database error occurs during the database creation.
        """
        try:
            song_name = self.string_checker(song_name)
            query = """
                    UPDATE Songs
                    SET deleted = 1
                    WHERE name = %s
                    """
            self.cursor.execute(query, (song_name, ))
            logger.info(f"{song_name} deleted")
        except mysql.connector.Error as err:
            logger.error(f"Error deleting a song {err}")
            raise DatabaseConnectionError(f"Error deleting a song {err}")
        
    def close_connection(self):
        self.cursor.close()
        self.conn.close()
        logger.info("Database connection closed.")

    def fetch_trending_songs(self):
        pass

