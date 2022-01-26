"""
This module provides action classes that can be put into a sequence
to create commands for cli object.
"""


from fintool.transac import TransactionManager
from fintool.logging import LoggingHelper


class Error(Exception):
    pass


class ActionError(Error):
    pass


class Action:
    def __init__(self):
        pass

    def exec(self):
        pass


class CreateTransaction(Action):
    """Create a Transaction instance from command data.
    """

    def __init__(self):
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)

    def exec(self, data):
        """Create a Transaction object and insert it into data.

        Args:
            data (dict): A dictionary containing required key-values to create
                            a transaction.
        """
        self._logger.debug(f'running action with: {data}')
        try:
            data["transaction"] = TransactionManager.create_transaction(data)
        except Exception as e:
            raise ActionError(e)


class SaveTransaction(Action):
    """Save a transaction in fintool db.
    """

    def __init__(self):
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)

    def exec(self, data):
        """Retrieve a transaction from data, serialize it and save it in fintool db.

        Args:
            data (dict): A dictionary containing a transaction.
        """
        self._logger.debug('running action with: {data}')
        try:
            TransactionManager.save_transaction(data["transaction"])
        except KeyError:
            raise ActionError("Missing input value: transaction")
