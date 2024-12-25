# Define paths
base_path = Path(__file__).resolve().parent.parent.parent
env_path = base_path / 'env_files' / 'special_detail.env'
log_dir = base_path / 'logger'
log_file = log_dir / 'app.log'

import mysql.connector
import os
from dotenv import load_dotenv
from pathlib import Path
import logging
import bcrypt
import sys

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
logger.debug(f"Loading .env file from: {env_path}")
load_dotenv(dotenv_path=env_path)

class User_model:
    def __init__(self, db_config: dict):
        """
        Initialize the UserModel class with database configuration.

        Args:
            db_config (dict): A dictionary containing database connection details.

        Raises:
                DatabaseConnectionError: If connection to the database fails
        """
        try:
            self.conn = mysql.connector.connect(**db_config)
            self.cursor = self.conn.cursor(dictionary=True)
            self.cursor.execute("SHOW COLUMNS FROM Users;")
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
        
    def hash_passwords(self, password: str) -> str:
        """
        Function to has passwords

        Args:
            password (str): Unhased password

        Returns:
            str: Hashed password
        """
        # Checks if input is a non empty space string
        password = self.string_checker(password)

        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify if a plain password matches the hashed password.
        Args:
            plain_password (str): User's plain text password.
            hashed_password (str): Stored hashed password.
        Returns:
            bool: True if the password matches, False otherwise.
        """
        # Checks if input is a non empty space string
        plain_password = self.string_checker(plain_password)

        # Checks if input is a non empty space string
        hashed_password = self.string_checker(hashed_password)

        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def register_user(self, user_data: dict):
        """
        Inserts a user into the Users database.

        Args:
            user_data (dict): A dictionary containing details about the user.
        Raises:
            InputError: If the set of columns does not equal the columns from the table.
            DatabaseConnectionError: If the database connection fails.
        """
        try:
            columns_table = [row["Field"] for row in self.table_columns]
            columns_dict = [col for col in user_data.keys()]
            excluded_cols = ["id", "deleted"]

            # Check if the table columns match the input columns
            self.check_if_input_cols_match(table_columns=columns_table, input_columns=columns_dict, exclude_columns=excluded_cols)

            input_columns_string = ", ".join(user_data.keys())
            placeholders = ", ".join(["%s"] * len(user_data))

            query = f"""
                        INSERT INTO `Users`({input_columns_string}) 
                        VALUES({placeholders});
                    """
            user_data["password"] = self.hash_passwords(user_data["password"])
            user_data_tuple = tuple(user_data.values())
            self.cursor.execute(query, user_data_tuple)
            self.conn.commit()
            logger.info(f"User sucessfully registered!")
        except mysql.connector.Error as err:
            logger.error(f"Database connection failed {err}.")
            raise DatabaseConnectionError(f"Database connection failed {err}.")
        except mysql.connector.DataError as err:
            logger.error(f"Wrong data format: {err}")
            raise InputError(f"Wrong data format: {err}")

    def authenticate_user(self, user_dict: dict) -> bool:
        """
        Authenticates users login credentials
        Args:
            user_dict (dict): Contains users username and his password
        Returns:
            bool: True if the password for the user matches, False otherwise.
        Raises: InputError: If user_dict is has more than two key-value pairs.
                            If in the dict you have different columns than username and password.
                            If the password or username is empty.
                DatabaseConnectionError: If connection to the database fails.
        """      
        try:
            ALLOWED_COLUMNS = ["username", "password"]

            columns = [col for col in user_dict.keys()]
            values = [val for val in user_dict.values()]
            
            self.check_if_input_cols_match(table_columns=ALLOWED_COLUMNS, input_columns=columns)
            
            if any(not value for value in values):
                logger.error("Username or password cannot be empty.")
                raise InputError("Username or password cannot be empty.")

            query = """
                    SELECT password FROM Users
                    WHERE username = %s;
                    """
            self.cursor.execute(query, (user_dict["username"], ))
            result = self.cursor.fetchone()
            
            if not result:
                logger.info(f"Authentication failed: {user_dict['username']} does not exist.")
                return False
            
            checked_password = self.verify_password(plain_password=user_dict["password"], hashed_password=result["password"])
            
            if checked_password:
                logger.info(f"{user_dict['username']} was authenticated")
            else:
                logger.info(f"{user_dict['username']} was not authenticated. Password was incorrect.")
            
            return checked_password
        except mysql.connector.Error as err:
            logger.error(f"Database connection failed {err}.")
            raise DatabaseConnectionError(f"Database connection failed {err}")
    
    def update_user_details(self, updated_info: dict, username: str):
        """
        Update a single detail in Users table
        
        Args:
            updated_info (dict): Dictionary containing the column to be updated and the desired value
                Example: {"email": "my_email@google.com"}
            username (string): Name of the user being updated.
                Example: "my_name"
        Raises:
            InputError: If dict has more than one key-value pair.
                        If a column passed in the dict is not in the table.
            DatabaseConnectionError: If database connection error occurs.
        """
        try:
            column_table = [row["Field"] for row in self.table_columns]

            column_dict, value = next(iter(updated_info.items()))

            # Check if input is a string
            username = self.string_checker(username)
            
            if  len(updated_info) != 1:
                logger.error("Dictionary doesnt have just one key-value pair")
                raise InputError("Dictionary doesnt have just one key-value pair")

            self.check_if_input_cols_match(table_columns=column_table, input_columns=column_dict, exact_match=False)

            if column_dict == "password":
                value = self.hash_passwords(value)

            query = f"""
                    UPDATE `Users`
                    SET {column_dict} = %s
                    WHERE username = %s;
                    """
            self.cursor.execute(query, (value, username))
            self.conn.commit()
            logger.info(f"{column_dict} has been updated to {value} for {username}")

        except mysql.connector.Error as err:
            logger.error(f"Database connection failed {err}.")
            raise DatabaseConnectionError(f"Database connection failed {err}.")

    def fetch_all_users(self) -> list:
        """
        Fetches all artists from the database.

        Args:
            None
        Returns:
            all_users (list): Return all the non deleted users from the database. Returns a empty list if no users are found.
        Raises:
            DatabaseConnectionError: If database error occurs during the database creation
        """
        try:
            query = """
                    SELECT username FROM non_deleted_users;
                    """
            self.cursor.execute(query)
            all_users_fetched = self.cursor.fetchall()

            if not all_users_fetched:
                logger.error("No users found")
                return []

            all_users = [row['username'] for row in all_users_fetched]
            logger.info("All users fetched")
            return all_users
        
        except mysql.connector.Error as err:
            logger.error(f"Databse connection failed {err}")
            raise DatabaseConnectionError(f"Databse connection failed {err}")
    
    def soft_delete_user_account(self, username: str):
        """
        This function takes a users username as input and marks him as deleted in our database.

        Args:
            username (string): Name of a user.
                Example: "my_name"

        Raises:
            ValueError: If username is not a string.
            DatabaseConnectionError: If database error occurs during the database creation.
        """

        try:
            # Checks if input is a non empty space string
            username = self.string_checker(username)
            
            query = """
                    UPDATE `Users`
                    SET deleted = 1
                    WHERE username = %s;
                    """
            self.cursor.execute(query, (username,))
            self.conn.commit()
            logger.info(f"{username} has been successfully deleted")

        except mysql.connector.Error as err:
            logger.error(f"Database connection failed {err}.")
            raise DatabaseConnectionError(f"Database connection failed {err}")

    def close_connection(self):
        self.cursor.close()
        self.conn.close()
        logger.info("Database connection closed.")
        