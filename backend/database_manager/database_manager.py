from pathlib import Path
# Define paths
base_path = Path(__file__).resolve().parent.parent.parent
env_path = base_path / 'env_files' / 'special_detail.env'
log_dir = base_path / 'logger'
log_file = log_dir / 'app.log'

import mysql.connector
from dotenv import load_dotenv
import os
import logging
import sys

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

load_dotenv(dotenv_path=env_path)

sys.path.append(str(base_path))

from utils.errors import InputError
from utils.errors import DatabaseConnectionError

class DatabaseManager:
    def __init__(self, db_config):
        """
        Initialize the DatabaseManager class with database configuration.

        Args:
            db_config (dict): A dictionary containing database connection details.
        """
        try:
            self.conn = mysql.connector.connect(**db_config)
            self.cursor = self.conn.cursor(dictionary=True)
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to the database: {err}")
            raise DatabaseConnectionError(f"Error connecting to the database: {err}")

    def get_cursor(self):
        """
        Get the database cursor.

        Returns:
            mysql.connector.cursor_cext.CMySQLCursorDict: The database cursor.
        """
        return self.cursor

    def rollback(self):
        """
        Rollback the current transaction.

        Raises:
            DatabaseConnectionError: If there is an error committing the transaction.
        """
        try:
            self.conn.rollback()
            logger.info("Rollback succesful!")
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to the database: {err}")
            raise DatabaseConnectionError(f"Error connecting to the database: {err}")

    def commit(self):
        """
        Commit the current transaction.

        Raises:
            DatabaseConnectionError: If there is an error committing the transaction.
        """

        try:
            self.conn.commit()
            logger.info("Commit succesful!")
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to the database: {err}")
            raise DatabaseConnectionError(f"Error connecting to the database: {err}")

    def close(self):
        """
        Close the database connection and cursor.
        """
        self.cursor.close()
        self.conn.close()

if __name__ == "__main__":

    db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

    db_manager = DatabaseManager(db_config=db_config)