
class InputError(Exception):
    """Custom exception built in to handle InputErrors
    """
    def __init__(self, message):
        """_summary_

        Args:
            message (str): message to let the developer know what error happend.
                        Example: "Wrong column input"
        """
        self.message = message
        super().__init__(self.message)

    def __str__(self):

        return self.message
    
class DatabaseConnectionError(Exception):
    """Custom exception built in to handle database errors
    """
    def __init__(self, message):
        """_summary_

        Args:
            message (str): message to let the developer know what error happend.
                        Example: "Database connection failed"
        """
        self.message = message
        super().__init__(self.message)

    def __str__(self):

        return self.message