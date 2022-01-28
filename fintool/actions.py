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


class CreateFilters(Action):
    """Convert cli options into filters dictionary.
    """
    def __init__(self):
        self.TYPE = 'type'
        self.DATE = 'date'
        self.AMOUNT = 'amount'
        self.TAGS = 'tags'
        self.FILTERS = 'filters'
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)

    def exec(self, data):
        """Create a dictionary with filters from cli options.
        """
        self._logger.debug('running action with: {data}')
        filters = {}
        if data[self.TYPE]:
            filters[self.TYPE] = data[self.TYPE]

        if data[self.DATE]:
            filters[self.DATE] = data[self.DATE]

        if data[self.AMOUNT]:
            filters[self.AMOUNT] = data[self.AMOUNT]

        if data[self.TAGS]:
            filters[self.TAGS] = f"{data[self.TAGS].split(',')}"

        if filters:
            data[self.FILTERS] = filters


class GetTransactions(Action):
    """Retrieve transactions from db using a set of filters.
    """
    def __init__(self):
        self.TRANSACTIONS = 'transactions'
        self.FILTERS = 'filters'
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)

    def exec(self, data):
        """Use TransactionManager to get transactions from db.
        """
        self._logger.debug('running action with: {data}')
        txs = TransactionManager.get_transactions(data.get(self.FILTERS))
        data[self.TRANSACTIONS] = txs


class PrintTransactions(Action):
    """Print transactions to stdout
    """
    def __init__(self):
        self.TRANSACTIONS = 'transactions'
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)

    def exec(self, data):
        """Get transactions from data object and print them to stdout.
        """
        self._logger.debug('running action with: {data}')
        print(data[self.TRANSACTIONS])
