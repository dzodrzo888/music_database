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
from user_model import User_model

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
logger.debug(f"Loading .env file from: {env_path}")
load_dotenv(dotenv_path=env_path)

class Payment_model:

    def __init__(self, cursor, db_man):
        """
        Initialize the Payment_model class with database configuration.

        Args:
            db_config (dict): A dictionary containing database connection details.

        Raises:
                DatabaseConnectionError: If connection to the database fails
        """
        try:
            self.cursor = cursor
            self.db_man = db_man
            self.cursor.execute("SHOW COLUMNS FROM User_subscriptions;")
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
        
    def insert_payment(self, payment_info: dict):
        """
        Insert payment information into the Payments table.

        Args:
            payment_info (dict): Dictionary containing payment information.

        Raises:
            DatabaseConnectionError: If connection to the database fails.
            InputError: If the input data is incorrect.
        """
        try:
            self.cursor.execute("SHOW COLUMNS FROM Payments;")
            table_columns = self.cursor.fetchall()
            table_columns_list = [col["Field"] for col in table_columns]
            exclude_cols = ["id", "date"]
            self.check_if_input_cols_match(table_columns=table_columns_list, input_columns=payment_info.keys(), exclude_columns=exclude_cols, exact_match=True)

            input_cols = ", ".join(payment_info.keys())
            placeholders = ", ".join(["%s"] * len(payment_info.keys()))

            query = f"""
                    INSERT INTO Payments ({input_cols})
                    VALUES ({placeholders});
                    """
            payment_tuple = tuple(payment_info.values())
            self.cursor.execute(query, payment_tuple)
            logger.info(f"Payment inserted: {payment_info}")
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to the database: {err}")
            raise DatabaseConnectionError(f"Error connecting to the database: {err}")
        except mysql.connector.DataError as err:
            logger.error(f"Wrong data format: {err}")
            raise InputError(f"Wrong data format: {err}")

    def insert_subscription(self, user_sub_info: dict):
        """
        Insert subscription information into the User_subscriptions table.

        Args:
            user_sub_info (dict): Dictionary containing payment information.

        Raises:
            DatabaseConnectionError: If connection to the database fails.
            InputError: If the input data is incorrect.
        """
        try:
            exclude_cols = ["id", "start_date", "expiration_date"]
            self.check_if_input_cols_match(table_columns=self.table_columns_list, input_columns=user_sub_info.keys(), exclude_columns=exclude_cols, exact_match=True)

            input_cols = ", ".join(user_sub_info.keys())
            placeholders = ", ".join(["%s"] * len(user_sub_info.keys()))
            query = f"""
                    INSERT INTO User_subscriptions ({input_cols})
                    VALUES ({placeholders});
                    """
            user_sub_tuple = tuple(user_sub_info.values())
            self.cursor.execute(query, user_sub_tuple)
            logger.info(f"Subscription inserted: user_id={user_sub_info["user_id"]}, subscription_plan_id={user_sub_info["subscription_plan_id"]}")
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to the database: {err}")
            raise DatabaseConnectionError(f"Error connecting to the database: {err}")
        except mysql.connector.DataError as err:
            logger.error(f"Wrong data format: {err}")
            raise InputError(f"Wrong data format: {err}")

    def fetch_purchase_info(self, subscription_info: dict) -> tuple:
        
        
        try:
            # Get the users username
            query_user = """
                    SELECT username
                    FROM Users 
                    WHERE id = %s;
                    """
            self.cursor.execute(query_user, (subscription_info["user_id"], ))
            username_dict = self.cursor.fetchone()

            # Get the subscription price
            query_price = """
                    SELECT price
                    FROM Subscription_plan_info
                    WHERE id = %s;
                    """
            self.cursor.execute(query_price, (subscription_info["subscription_plan_id"], ))
            price_dict = self.cursor.fetchone()   

            payment_dict = {
                "user_id": subscription_info["user_id"],
                "money_value": price_dict["price"]
            }     

            return (payment_dict, username_dict["username"])
        except mysql.connector.Error as err:
            self.conn.rollback()
            logger.error(f"Error connecting to the database: {err}")
            raise DatabaseConnectionError(f"Error connecting to the database: {err}")
        
    def update_user_to_premium(self, username: str):
        """
        Function to simply initialize User_model class and then change the type of the user to premium.

        Args:
            username (str): Users username
        """
        user_model = User_model(self.cursor)
        user_model.update_user_details(updated_info={"user_type": "premium"}, username=username)

    def subscription_plan_purchase(self, subscription_info: dict):
        """
        Using a transaction this function inserts user info into subscriptions, payments and updates user to be a preimum user.

        Args:
            subscription_info (dict): Dict containing info about the user and subscription he bought.

        Raises:
            DatabaseConnectionError: If connection to the database fails
        """
        
        try:
            if db_manager.conn.in_transaction:
                logger.warning("Transaction already in progress. Rolling back before starting a new one.")
                db_manager.rollback()

            db_manager.conn.start_transaction()

            # Insert subscription information
            self.insert_subscription(subscription_info)

            payment_info, username = self.fetch_purchase_info(subscription_info=subscription_info)

            # Insert payment information
            self.insert_payment(payment_info)

            # Change user type to premium also commits the update
            self.update_user_to_premium(username=username)

            logger.info(f"User ID {subscription_info["user_id"]} purchased subscription plan ID {subscription_info["subscription_plan_id"]}")

        except mysql.connector.Error as err:
            db_manager.rollback()
            logger.error(f"Error connecting to the database: {err}")
            raise DatabaseConnectionError(f"Error connecting to the database: {err}")

    def fetch_users_subscription_plan(self, username: str) -> list:
        """
        Fetches users subsription plan and when it expires

        Args:
            username(str): Users username

        Raises:
            ValueError: If string is not inputed
            DatabaseConnectionError: If database error occurs during the database creation
        """
        try:
            username = self.string_checker(username)
            query = """
                    SELECT u.username AS Username, s.plan_name AS Subscription_plan, us.expiration_date AS Expritaion_date
                    FROM Users AS u
                    JOIN User_subscriptions AS us ON u.id = us.user_id
                    JOIN Subscription_plan_info AS s ON s.id = us.subscription_plan_id
                    WHERE u.username = %s
                    """
            self.cursor.execute(query, (username, ))
            user_subscription_info = self.cursor.fetchall()
            return user_subscription_info
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to the database: {err}")
            raise DatabaseConnectionError(f"Error connecting to the database: {err}")

    def fetch_payment_details(self, username: str) -> list:
        """
        Fetches users payment details.

        Args:
            username(str): Users username

        Raises:
            ValueError: If string is not inputed
            DatabaseConnectionError: If database error occurs during the database creation
        """
        try:
            username = self.string_checker(username)
            query = """
                    SELECT u.username AS Username, p.date AS Payment_date, p.money_value AS Total
                    FROM Users AS u
                    JOIN Payments AS p ON u.id = p.user_id
                    WHERE u.username = %s
                    """
            self.cursor.execute(query, (username, ))
            user_payment_info = self.cursor.fetchall()
            return user_payment_info
        except mysql.connector.Error as err:
            logger.error(f"Error connecting to the database: {err}")
            raise DatabaseConnectionError(f"Error connecting to the database: {err}")


if __name__ == "__main__":

    subscription_info = {
        "user_id": 2,
        "subscription_plan_id": 2
    }

    db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
    }

    db_manager = DatabaseManager(db_config=db_config)

    payment_model = Payment_model(db_manager.get_cursor(), db_manager)

    payment_model.subscription_plan_purchase(subscription_info)
    db_manager.commit()
    db_manager.close()

