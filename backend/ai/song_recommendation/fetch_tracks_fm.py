import time
from dotenv import load_dotenv
from pathlib import Path
import os
import requests
import mysql.connector
import sys
import logging


base_path = Path(__file__).resolve().parent.parent.parent.parent
env_path = base_path / 'env_files' / 'ai_db_detail.env'
log_dir = base_path / 'logger'
log_file =  log_dir / 'app.log'

load_dotenv(dotenv_path=env_path)

sys.path.append(str(base_path))

from utils.errors import InputError
from utils.errors import DatabaseConnectionError
from backend.database_manager.database_manager import DatabaseManager

logging.basicConfig(
    level=logging.DEBUG,  # Set the log level to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Log format
    handlers=[
        logging.FileHandler(log_file),  # Log to a file named app.log in the logs directory
        logging.StreamHandler()  # Also log to the console
    ]
)

logger = logging.getLogger(__name__)

# Spotify API credentials
API_KEY = os.getenv('API_KEY_fm')
SHARED_SECRET = os.getenv('SHARED_SECRET_fm')
REDIRECT_URI = os.getenv('REDIRECT_URI_fm')
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

class track_info_fetch:
    
    def __init__(self, cursor, conn):
        """
        Initialize the UserModel class with database configuration.

        Args:
            cursor (mysql.connector.cursor_cext.CMySQLCursorDict): The database cursor.

        Raises:
                DatabaseConnectionError: If connection to the database fails
        """
        try:
            self.cursor = cursor
            self.conn = conn
            self.cursor.execute("SHOW COLUMNS FROM Tracks;")
            self.table_columns = self.cursor.fetchall()
            logger.info("Database connection established successfully.")
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to the database: {err}")
            raise DatabaseConnectionError(f"Error connecting to the database: {err}")
        
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

    def fetch_top_tags(self, limit=100):
        """Fetch the top tags (genres)."""
        url = (
            f"http://ws.audioscrobbler.com/2.0/?method=chart.gettoptags"
            f"&api_key={API_KEY}&format=json&limit={limit}"
        )
        response = requests.get(url)
        if response.status_code == 200:
            tags = response.json()["tags"]["tag"]
            return [tag["name"] for tag in tags]
        else:
            print(f"Error fetching top tags: {response.status_code}")
            return []

    def fetch_top_artists_by_tag(self, tag, limit=100):
        """Fetch the top artists for a given tag."""
        url = (
            f"http://ws.audioscrobbler.com/2.0/?method=tag.gettopartists"
            f"&tag={tag}&api_key={API_KEY}&format=json&limit={limit}"
        )
        response = requests.get(url)
        if response.status_code == 200:
            artists = response.json()["topartists"]["artist"]
            return [artist["name"] for artist in artists]
        else:
            print(f"Error fetching artists for tag {tag}: {response.status_code}")
            return []

    def fetch_top_tracks_by_artist(self, artist, genre, limit=5, max_fetch=50):
        """Fetch the top tracks for a given artist, skipping tracks without an mbid."""
        url = (
            f"http://ws.audioscrobbler.com/2.0/?method=artist.gettoptracks"
            f"&artist={artist}&api_key={API_KEY}&format=json&limit={max_fetch}"
        )
        response = requests.get(url)
        if response.status_code == 200:
            response_data = response.json()
            if "toptracks" in response_data and "track" in response_data["toptracks"]:
                
                tracks = response_data["toptracks"]["track"]
                filtered_tracks = [
                    {"mbid": track["mbid"], "name": track["name"], "artist_name": artist, "genre": genre}
                    for track in tracks
                    if "mbid" in track and track["mbid"]
                ]

                if len(filtered_tracks) >= limit:
                    return filtered_tracks[:limit]
                else:
                    return filtered_tracks
            else:
                print(f"No 'toptracks' found for artist: {artist}")
                return []
        else:
            print(f"Error fetching top tracks for artist {artist}: {response.status_code}")
            return []
        
    def track_insertion(self, track_info: dict):
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
            columns_dict = [col for col in track_info.keys()]
            excluded_cols = ["id"]

            # Check if the table columns match the input columns
            self.check_if_input_cols_match(table_columns=columns_table, input_columns=columns_dict, exclude_columns=excluded_cols)

            input_columns_string = ", ".join(track_info.keys())
            placeholders = ", ".join(["%s"] * len(track_info))
            query = f"""
                        INSERT INTO `Tracks`({input_columns_string}) 
                        VALUES({placeholders});
                    """
            track_info_tuple = tuple(track_info.values())
            self.cursor.execute(query, track_info_tuple)
            logger.info(f"New track added {track_info["name"]}")
        except mysql.connector.Error as err:
            logger.error(f"Error when createing a new track {err}")
            raise DatabaseConnectionError(f"Database connection failed {err}.")

    def main(self):
        genres = self.fetch_top_tags(limit=100)
        print(f"Fetched {len(genres)} genres.")

        for genre in genres:
            print(f"Fetching artists for genre: {genre}")
            artists = self.fetch_top_artists_by_tag(genre, limit=100)
            
            for artist in artists:
                print(f"Fetching tracks for artist: {artist}")
                tracks = self.fetch_top_tracks_by_artist(artist, genre, limit=5)
                if tracks:
                    for track in tracks:
                        self.track_insertion(track)
                        self.conn.commit()
                
                time.sleep(0.5)

            time.sleep(1)

if __name__ == "__main__":
    db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
    }

    db_manager = DatabaseManager(db_config=db_config)
    track_fetch = track_info_fetch(db_manager.get_cursor(), db_manager.conn)
    
    track_fetch.main()
