from pathlib import Path
# Define paths
base_path = Path(__file__).resolve().parent.parent.parent
env_path = base_path / 'env_files' / 'special_detail.env'
log_dir = base_path / 'logger'
log_file = log_dir / 'app.log'

import mysql.connector
import os
from dotenv import load_dotenv
import logging
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

class Subscription_model:

    def __init__(self, db_config):
        """
        Initialize the Payment_model class with database configuration.

        Args:
            db_config (dict): A dictionary containing database connection details.

        Raises:
                DatabaseConnectionError: If connection to the database fails
        """
        try:
            self.conn = mysql.connector.connect(**db_config)
            self.cursor = self.conn.cursor(dictionary=True)
            self.cursor.execute("SHOW COLUMNS FROM Subscription_plan_info;")
            self.table_columns = self.cursor.fetchall()
            self.table_columns_list = [col["Field"] for col in self.table_columns]
            logger.info("Connection to the database succesful")
        except mysql.connector.Error as err:
            logger.error(f"Connection to the database failed: {err}")
            raise DatabaseConnectionError(f"Connection to the database failed: {err}")
    
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
    
    def add_new_plan(self, subscription_dict: dict):
        """
        Function that adds a new plan to my subscriptions table.
        
        Args:
            subscription_dict(dict): Dictionary containing information about the subscription.

        Raises:
            DatabaseConnectionError: If connection to the database fails.
            InputError: If the set of columns does not equal the columns from the table.
                        If the wrong data type is inputed.        
        """
        
        try:
            exclude_columns = ["id", "deleted"]
            self.check_if_input_cols_match(table_columns=self.table_columns_list, input_columns=subscription_dict.keys(), exclude_columns=exclude_columns)

            input_cols = ", ".join(subscription_dict.keys())
            placeholders = ", ".join(["%s"] * len(subscription_dict.keys()))

            query = f"""
                    INSERT INTO `Subscription_plan_info` ({input_cols})
                    VALUES({placeholders});
                    """
            subscription_tuple = tuple(subscription_dict.values())
            self.cursor.execute(query, subscription_tuple)
            self.conn.commit()
            logger.info(f"Subscription plan: {subscription_dict["plan_name"]} inserted")
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to the database: {err}")
            raise DatabaseConnectionError(f"Error connecting to the database: {err}")
        except mysql.connector.DataError as err:
            logger.error(f"Wrong data format: {err}")
            raise InputError(f"Wrong data format: {err}")
        
    def update_subscription_info(self, updated_info: dict, subscription: str):
        """
        Update a single detail in Subscription_plan_info table
        
        Args:
            updated_info (dict): Dictionary containing the column to be updated and the desired value
                Example: {"email": "my_email@google.com"}
            subscription (string): Name of the subscription being updated.
                Example: "my_name"
        Raises:
            InputError: If dict has more than one key-value pair.
                        If a column passed in the dict is not in the table.
                        If a value doesnt match the table value
            DatabaseConnectionError: If database connection error occurs.
        """
        try:
            # Check if input is a string
            subscription = self.string_checker(subscription)
            
            column, value = next(iter(updated_info.items()))

            if  len(updated_info) != 1:
                logger.error("Dictionary doesnt have just one key-value pair")
                raise InputError("Dictionary doesnt have just one key-value pair")

            self.check_if_input_cols_match(table_columns=self.table_columns_list, input_columns=column, exact_match=False)

            query = f"""
                    UPDATE `Subscription_plan_info`
                    SET {column} = %s
                    WHERE plan_name = %s;
                    """
            updated_info_tuple = (value, subscription)
            self.cursor.execute(query, updated_info_tuple)
            self.conn.commit()
            logger.info(f"Subscription plan: {subscription} updated")
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to the database: {err}")
            raise DatabaseConnectionError(f"Error connecting to the database: {err}")
        except mysql.connector.DataError as err:
            logger.error(f"Wrong data format: {err}")
            raise InputError(f"Wrong data format: {err}")
        
    def fetch_specific_subscription(self, subscription: str) -> list:
        """
        Fetches specific subscriptions from the database.

        Args:
            None
        Returns:
            specific_subscription (list): Return specific non deleted subscriptions from the database. Returns a empty list if the specific subscription is not found.
        Raises:
            DatabaseConnectionError: If database error occurs during the database creation
        """
        try:
            query = """
                    SELECT * FROM non_deleted_subscriptions
                    WHERE plan_name = %s;
                    """
            self.cursor.execute(query, (subscription, ))
            specific_subscription = self.cursor.fetchall()

            if not specific_subscription:
                logger.error("No subscription found")
                return []

            logger.info("Subscription fetched")
            return specific_subscription
        
        except mysql.connector.Error as err:
            logger.error(f"Databse connection failed {err}")
            raise DatabaseConnectionError(f"Databse connection failed {err}")
    
    def fetch_all_subscriptions(self) -> list:
        """
        Fetches all subscriptions from the database.

        Args:
            None
        Returns:
            all_subscriptions (list): Return all the non deleted subscriptions from the database. Returns a empty list if no subscriptions are found.
        Raises:
            DatabaseConnectionError: If database error occurs during the database creation
        """
        try:
            query = """
                    SELECT * FROM non_deleted_subscriptions;
                    """
            self.cursor.execute(query)
            all_subscription_fetched = self.cursor.fetchall()

            if not all_subscription_fetched:
                logger.error("No subscriptions found")
                return []

            logger.info("All subscriptions fetched")
            return all_subscription_fetched
        
        except mysql.connector.Error as err:
            logger.error(f"Databse connection failed {err}")
            raise DatabaseConnectionError(f"Databse connection failed {err}")
        
    def soft_delete_user_account(self, subscription: str):
        """
        This function takes a subscription name as input and marks it as deleted in our database.

        Args:
            subscription (string): Name of a subscription.
                Example: "my_name"

        Raises:
            ValueError: If subscription is not a string.
            DatabaseConnectionError: If database error occurs during the database creation.
        """

        try:
            # Checks if input is a non empty space string
            subscription = self.string_checker(subscription)
            
            query = """
                    UPDATE `Users`
                    SET deleted = 1
                    WHERE username = %s;
                    """
            self.cursor.execute(query, (subscription,))
            self.conn.commit()
            logger.info(f"{subscription} has been successfully deleted")

        except mysql.connector.Error as err:
            logger.error(f"Database connection failed {err}.")
            raise DatabaseConnectionError(f"Database connection failed {err}")

    
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

subscription = {
    "plan_name": "Cool student plan",
    "price": 100,
    "duration": 360
}

subscription_model = Subscription_model(db_config=db_config)

subscription_model.close_connection()
