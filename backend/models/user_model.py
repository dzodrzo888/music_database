import mysql.connector
import os
from dotenv import load_dotenv
from pathlib import Path
import logging
import bcrypt

# Define paths
base_path = Path(__file__).resolve().parent.parent.parent
env_path = base_path / 'env_files' / 'special_detail.env'
log_dir = base_path / 'logger'
log_file = log_dir / 'app.log'

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
        """
        try:
            self.conn = mysql.connector.connect(**db_config)
            self.cursor = self.conn.cursor(dictionary=True)
            logger.info("Database connection established successfully.")
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to the database: {err}")
            raise

    def string_checker(self, string: str):
        """
        Function to check if a input is a string

        Args:
            string (str): Any string to be checked.
                        Example: "a"

        Raises:
            ValueError: If input is not a string.
        """


        if not isinstance(string, str):
            logger.error("Input is not a string!")
            raise ValueError("Input must be a non-empty string.")

        if not string.strip():
            logger.error("Input must be a non empty string")

    def check_if_input_cols_match(self, table_columns: list, input_columns: list, exclude_columns = None):
        """
        Checks if columns that want to be inputed match the table columns raises a ValueError if not.

        Args:
            table_columns (list): List of columns from a sql table,
            input_columns (list): List of columns that want to be inputed.

        Raises:
            ValueError: If the columns dont match.
        """

        if not exclude_columns:
            exclude_columns = []

        table_columns_filtered = [col for col in table_columns if col not in exclude_columns]

        if set(input_columns) != set(table_columns_filtered):
                logger.error(f"Inputed columns dont match the table columns")
                raise ValueError ("Inputed columns dont match the table columns")
        
    def hash_passwords(self, password: str) -> str:
        """
        Function to has passwords

        Args:
            password (str): Unhased password

        Returns:
            str: Hashed password
        """
        # Checks if input is a non empty space string
        self.string_checker(password)

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
        self.string_checker(plain_password)

        # Checks if input is a non empty space string
        self.string_checker(hashed_password)

        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def register_user(self, user_data: dict):
        """
        Inserts a user into the Users database.

        Args:
            user_data (dict): A dictionary containing details about the user.
        Raises:
            ValueError: If the set of columns does not equal the columns from the table.
            RuntimeError: If the database connection fails.
        """
        try:
            self.cursor.execute("SHOW COLUMNS FROM Users;")
            columns_table = [row["Field"] for row in self.cursor.fetchall()]
            columns_dict = [col for col in user_data.keys()]
            excluded_cols = ["id", "deleted"]

            # Check if the table columns match the input columns
            self.check_if_input_cols_match(table_columns=columns_table, input_columns=columns_dict, exclude_columns=excluded_cols)

            query = """
                        INSERT INTO `Users`(username, password, email, date_of_birth, profile_image) 
                        VALUES(%s, %s, %s, %s, %s)
                    """
            user_data["password"] = self.hash_passwords(user_data["password"])
            user_data_tuple = tuple(user_data.values())
            self.cursor.execute(query, user_data_tuple)
            self.conn.commit()
            logger.info(f"User sucessfully registered!")
        except mysql.connector.Error as err:
            logger.error(f"Database connection failed {err}.")
            raise RuntimeError(f"Database connection failed {err}.")

    def authenticate_user(self, user_dict: dict) -> bool:
        """
        Authenticates users login credentials
        Args:
            user_dict (dict): Contains users username and his password
        Returns:
            bool: True if the password for the user matches, False otherwise.
        Raises: ValueError: If user_dict is has more than two key-value pairs.
                            If in the dict you have different columns than username and password.
                            If the password or username is empty.
                RuntimeError: If connection to the database fails.
        """      
        try:
            ALLOWED_COLUMNS = ["username", "password"]

            columns = [col for col in user_dict.keys()]
            values = [val for val in user_dict.values()]
            
            self.check_if_input_cols_match(table_columns=ALLOWED_COLUMNS, input_columns=columns)
            
            if any(not value for value in values):
                logger.error("Username or password cannot be empty.")
                raise ValueError("Username or password cannot be empty.")

            query = """
                    SELECT password FROM Users
                    WHERE username = %s
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
            raise RuntimeError(f"Database connection failed {err}")
    
    def update_user_details(self, updated_info: dict, username: str):
        """
        Update a single detail in Users table
        
        Args:
            updated_info (dict): Dictionary containing the column to be updated and the desired value
                Example: {"email": "my_email@google.com"}
            username (string): Name of the user being updated.
                Example: "my_name"
        Raises:
            ValueError: If dict has more than one key-value pair.
                        If a column passed in the dict is not in the table.
            RuntimeError: If database connection error occurs.
        """
        try:
            self.cursor.execute("SHOW COLUMNS FROM Users;")
            column_table = [row["Field"] for row in self.cursor.fetchall()]

            column_dict, value = next(iter(updated_info.items()))

            # Check if input is a string
            self.string_checker(username)
            
            if  len(updated_info) != 1:
                logger.error("Dictionary doesnt have just one key-value pair")
                raise ValueError("Dictionary doesnt have just one key-value pair")

            if column_dict not in column_table:
                logger.error(f"{column_dict} is not in table columns")
                raise ValueError(f"{column_dict} is not in table columns")

            if column_dict == "password":
                value = self.hash_passwords(value)

            query = f"""
                    UPDATE `Users`
                    SET {column_dict} = %s
                    WHERE username = %s
                    """
            self.cursor.execute(query, (value, username))
            self.conn.commit()
            logger.info(f"{column_dict} has been updated to {value} for {username}")

        except mysql.connector.Error as err:
            logger.error(f"Database connection failed {err}.")
            raise RuntimeError(f"Database connection failed {err}.")

    def fetch_all_users(self):
        """
        Fetches all artists from the database.

        Args:
            None
        Returns:
            all_users (list): Return all the non deleted users from the database. Returns a empty list if no users are found.
        Raises:
            RuntimeError: If database error occurs during the database creation
        """
        try:
            query = """
                    SELECT * FROM non_deleted_users
                    """
            self.cursor.execute(query)
            all_users_fetched = self.cursor.fetchall()

            if not all_users_fetched:
                logger.error("No users found")
                return []

            all_users = [row['username'] for row in all_users_fetched]
            logger.info("All artists fetched")
            return all_users
        
        except mysql.connector.Error as err:
            logger.error(f"Databse connection failed {err}")
            raise RuntimeError(f"Databse connection failed {err}")
    
    def delete_user_account(self, username: str):
        """
        This function takes a users username as input and marks him as deleted in our database.

        Args:
            username (string): Name of a user.
                Example: "my_name"

        Raises:
            ValueError: If username is not a string.
            RuntimeError: If database error occurs during the database creation.
        """

        try:
            # Checks if input is a non empty space string
            self.string_checker(username)
            
            query = """
                    UPDATE `Users`
                    SET deleted = 1
                    WHERE username = %s
                    """
            self.cursor.execute(query, (username,))
            self.conn.commit()
            logger.info(f"{username} has been successfully deleted")

        except mysql.connector.Error as err:
            logger.error(f"Database connection failed {err}.")
            raise RuntimeError(f"Database connection failed {err}")

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