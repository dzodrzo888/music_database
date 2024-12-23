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

class Playlist_model:

    def __init__(self, db_config: dict):
        """
        Initialize the Playlist_model class with database configuration.

        Args:
            db_config (dict): A dictionary containing database connection details.

        Raises:
                DatabaseConnectionError: If connection to the database fails.
        """
        try:
            self.conn = mysql.connector.connect(**db_config)
            self.cursor = self.conn.cursor(dictionary=True)
            self.cursor.execute("SHOW COLUMNS FROM Playlists;")
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
        
    def add_new_playlist(self, playlist_info: dict):
        """
        Inserts a playlist into the Playlists database.

        Args:
            playlist_info (dict): A dictionary containing details about the playlist.
            
        Raises:
            InputError: If the set of columns does not equal the columns from the table.
            DatabaseConnectionError: If the database connection fails.
        """
        try:
            columns_table = [row["Field"] for row in self.table_columns]
            columns_dict = [col for col in playlist_info.keys()]
            excluded_cols = ["id", "deleted"]

            # Check if the table columns match the input columns
            self.check_if_input_cols_match(table_columns=columns_table, input_columns=columns_dict, exclude_columns=excluded_cols)

            input_columns_string = ", ".join(playlist_info.keys())
            placeholders = ", ".join(["%s"] * len(playlist_info))

            query = f"""
                        INSERT INTO `Playlists`({input_columns_string}) 
                        VALUES({placeholders});
                    """
            playlists_tuple = tuple(playlist_info.values())
            self.cursor.execute(query, playlists_tuple)
            self.conn.commit()
            logger.info(f"New song added {playlist_info["name"]}")
        except mysql.connector.Error as err:
            logger.error(f"Error when createing a new song {err}")
            raise DatabaseConnectionError(f"Database connection failed {err}.")

    def add_songs_to_playlist(self, song_id: str, playlist_id: str):
        """
        Adds songs to a playlist.

        Args:
            song_id (string): Songs id.
            Playlist_id (string): Playlist id.
        Raises:
            ValueError: If song_id or playlist_id is not a string
            DatabaseConnectionError: If database error occurs during the database creation
        """
        try:
            song_id = self.string_checker(song_id)
            playlist_id = self.string_checker(playlist_id)
            query = """
                    INSERT INTO Playlist_tracks(playlist_id, song_id)
                    VALUES(%s, %s)
                    """
            self.cursor.execute(query, (playlist_id, song_id))
            self.conn.commit()
            logger.info(f"New song added to the playlist {playlist_id}")
        except mysql.connector.Error as err:
            logger.error(f"Databse connection failed {err}")
            raise DatabaseConnectionError(f"Databse connection failed {err}")
    
    def remove_songs_from_playlist(self, song_id: str, playlist_id: str):
        """
        Remove songs to a playlist.

        Args:
            song_id (string): Songs id.
            Playlist_id (string): Playlist id.
        Raises:
            ValueError: If song_id or playlist_id is not a string
            DatabaseConnectionError: If database error occurs during the database creation
        """
        try:
            song_id = self.string_checker(song_id)
            playlist_id = self.string_checker(playlist_id)
            query = """
                    DELETE FROM Playlist_tracks
                    WHERE playlists_id = %s AND song_id = %s
                    """
            self.cursor.execute(query, (playlist_id, song_id))
            self.conn.commit()
            logger.info(f"Song removed from the playlist {playlist_id}")
        except mysql.connector.Error as err:
            logger.error(f"Databse connection failed {err}")
            raise DatabaseConnectionError(f"Databse connection failed {err}")

    def fetch_all_playlist_by_user(self, user_name: str) -> list:
        """
        Fetches all playlists for a user.

        Args:
            user_name (string): User name
        Returns:
            all_playlists (list): Return all the non deleted playlists for a user.
        Raises:
            ValueError: If user_name is not a string
            DatabaseConnectionError: If database error occurs during the database creation
        """
        try:
            user_name = self.string_checker(user_name)

            query = f"""
                    SELECT p.name AS Playlists FROM non_deleted_playlists AS p
                    JOIN Users AS u ON u.id = p.creator_id
                    WHERE u.name = {user_name}
                    """
            self.cursor.execute(query)
            all_playlists_fetched = self.cursor.fetchall()

            if not all_playlists_fetched:
                logger.warning("No playlists found for user")
                return []

            all_playlists = [row['name'] for row in all_playlists_fetched]
            logger.info("All playlists fetched")
            return all_playlists
        
        except mysql.connector.Error as err:
            logger.error(f"Databse connection failed {err}")
            raise DatabaseConnectionError(f"Databse connection failed {err}")

    def fetch_all_songs_from_playlist(self, playlist_name: str) -> list:
        """
        Fetches all songs from a playlist.

        Args:
            playlist_name (string): Playlist name
        Returns:
            all_songs (list): Return all the non deleted songs from the playlist.
        Raises:
            ValueError: If playlist_name is not a string
            DatabaseConnectionError: If database error occurs during the database creation
        """
        try:
            playlist_name = self.string_checker(playlist_name)

            query = f"""
                    SELECT s.name AS Songs FROM non_deleted_songs AS s
                    JOIN Playlist_tracks AS plt ON s.id = plt.song_id
                    JOIN non_deleted_playlists AS pl ON pl.id = plt.playlists_id
                    WHERE pl.name = {playlist_name}
                    """
            self.cursor.execute(query)
            all_songs_fetched = self.cursor.fetchall()

            if not all_songs_fetched:
                logger.warning("No Songs found in a playlist")
                return []

            all_songs = [row['name'] for row in all_songs_fetched]
            logger.info("All songs fetched")
            return all_songs
        
        except mysql.connector.Error as err:
            logger.error(f"Databse connection failed {err}")
            raise DatabaseConnectionError(f"Databse connection failed {err}")

    def share_playlist(self):
        pass

    def update_playlist_details(self, playlist_update_info: dict, playlist_name: str):
        """
        Function to update playlist info.

        Args:
            playlist_update_info (dict): dict containing the column and the value that will be changed for a playlist.
            playlist_name (str): Playlist name.
        
        Raises:
                InputError: If len of playlist_update info not 1.
                            if column is not in the songs table
                DatabaseConnectionError: If connection to the database fails
        """
        try:
            column_table = [row["Field"] for row in self.table_columns]

            column_dict, value = next(iter(playlist_update_info.items()))
            # Check if input is a string
            playlist_name = self.string_checker(playlist_name)
            
            if  len(playlist_update_info) != 1:
                logger.error("Dictionary doesnt have just one key-value pair")
                raise InputError("Dictionary doesnt have just one key-value pair")

            self.check_if_input_cols_match(table_columns=column_table, input_columns=column_dict, exact_match=False)
            
            query = f"""
                    UPDATE Playlists
                    SET {column_dict} = %s
                    WHERE name = %s
                    """
            self.cursor.execute(query, (value, playlist_name))
            self.conn.commit()
            logger.info(f"{playlist_name} info updated on {column_dict} to {value}")
        except mysql.connector.Error as err:
            logger.error(f"Error updating a song info {err}")
            raise DatabaseConnectionError(f"Error updating a song info {err}")

    def soft_delete_playlist(self, playlist_name: str):
        """
        This function takes a playlist name as input and marks him as deleted in our database.

        Args:
            playlist_name (string): Name of a playlist.
                Example: "Come together"

        Raises:
            ValueError: If playlist_name is not a string.
            DatabaseConnectionError: If database error occurs during the database creation.
        """
        try:
            playlist_name = self.string_checker(playlist_name)
            query = """
                    UPDATE Playlists
                    SET deleted = 1
                    WHERE name = %s
                    """
            self.cursor.execute(query, (playlist_name, ))
            self.conn.commit()
            logger.info(f"{playlist_name} deleted")
        except mysql.connector.Error as err:
            logger.error(f"Error deleting a song {err}")
            raise DatabaseConnectionError(f"Error deleting a song {err}")
    
    def close_connection(self):
        self.cursor.close()
        self.conn.close()
        logger.info("Database connection closed.")