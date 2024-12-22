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
            self.cursor = self.conn.cursor()
            logger.info("Database connection established successfully.")
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to the database: {err}")
            raise
        
    def hash_passwords(self, password: str) -> str:
        """
        Function to has passwords

        Args:
            password (str): Unhased password

        Returns:
            str: Hashed password
        """
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
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def register_user(self, user_data: dict):
        """
        Inserts a user into the Users database.

        Args:
            user_data (dict): A dictionary containing details about the user.
        """
        try:
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
            logger.error(f"Error inserting into the users table {err}.")
            raise

    def authenticate_user(self, user_dict: dict) -> bool:
        """
        Authenticates users login credentials
        Args:
            user_dict (dict): Contains users username and his password
        Returns:
            bool: True if the password for the user matches, False otherwise.
        """      
        try:
            query = """
                    SELECT password FROM Users
                    WHERE username = %s
                    """
            self.cursor.execute(query, (user_dict["username"], ))
            result = self.cursor.fetchone()
            if not result:
                logger.info(f"Authentication failed: {user_dict['username']} does not exist.")
                return False
            checked_password = self.verify_password(plain_password=user_dict["password"], hashed_password=result[0])
            if checked_password:
                logger.info(f"{user_dict['username']} was authenticated")
            else:
                logger.info(f"{user_dict['username']} was not authenticated")
            return checked_password
        except mysql.connector.Error as err:
            logger.error(f"Error when authenticating user {err}.")
            raise
    
    def update_user_details(self, updated_info: dict, username: str):
        """
        Update a single detail in Users table
        
        Args:
            updated_info (dict): Dictionary containing the column to be updated and the desired value
            username (string): Name of the user being updated
        """
        try:
            column, value = next(iter(updated_info.items()))

            query = f"""
                    UPDATE `Users`
                    SET {column} = %s
                    WHERE username = %s
                    """
            self.cursor.execute(query, (value, username))
            self.conn.commit()
            logger.info(f"{column} has been updated to {value} for {username}")
        except mysql.connector.Error as err:
            logger.error(f"Error updating user {err}.")
            raise
    
    def delete_user_account(self, username: str):
        """
        This function takes a users username as input and marks him as deleted in our database.

        Args:
            username (string): Name of a user.
        """

        try:
            query = """
                    UPDATE `Users`
                    SET deleted = 1
                    WHERE username = %s
                    """
            self.cursor.execute(query, (username,))
            self.conn.commit()
            logger.info(f"{username} has been successfully deleted")
        except mysql.connector.Error as err:
            logger.error(f"Error deleting user {err}.")
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
