"""
This module provides action classes that can be put into a sequence
to create commands for cli object.
"""


from fintool.transac import Transaction, TransactionManager
from fintool.logging import LoggingHelper
from fintool.stats import StatsHelper


class Error(Exception):
    pass


class ActionError(Error):
    pass


class Action:
    def __init__(self):
        pass

    def exec(self, data):
        pass


class CreateTransaction(Action):
    """Create a Transaction instance from command data.
    """

    def __init__(self):
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        super().__init__()

    def exec(self, data):
        """Create a Transaction object and insert it into data.

        Args:
            data (dict): A dictionary containing required key-values to create
                            a transaction.
        """
        self._logger.debug('running action with: %s', data)
        try:
            data["transaction"] = Transaction.from_dict(data)
        except Exception as exception:
            raise ActionError(exception)


class SaveTransaction(Action):
    """Save a transaction in fintool db.
    """

    def __init__(self):
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        super().__init__()

    def exec(self, data):
        """Retrieve a transaction from data, serialize it and save it in fintool db.

        Args:
            data (dict): A dictionary containing a transaction.
        """
        self._logger.debug('running action with: %s', data)
        transaction_manager = TransactionManager()
        try:
            transaction_manager.save_transaction(data["transaction"])
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
        super().__init__()

    def exec(self, data):
        """Create a dictionary with filters from cli options.
        """
        self._logger.debug('running action with: %s', data)
        filters = {}
        if data[self.TYPE]:
            filters[self.TYPE] = data[self.TYPE]

        if data[self.DATE]:
            filters[self.DATE] = data[self.DATE]

        if data[self.AMOUNT]:
            filters[self.AMOUNT] = data[self.AMOUNT]

        if data[self.TAGS]:
            filters[self.TAGS] = set(data[self.TAGS].split('|'))

        if filters:
            data[self.FILTERS] = filters


class GetTransactions(Action):
    """Retrieve transactions from db using a set of filters.
    """
    def __init__(self):
        self.TRANSACTIONS = 'transactions'
        self.FILTERS = 'filters'
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        super().__init__()

    def exec(self, data):
        """Use TransactionManager to get transactions from db.
        """
        self._logger.debug('running action with: %s', data)
        transaction_manager = TransactionManager()
        txs = transaction_manager.get_transactions(data.get(self.FILTERS))
        data[self.TRANSACTIONS] = txs


class PrintTransactions(Action):
    """Print transactions to stdout
    """
    def __init__(self):
        self.TRANSACTIONS = 'transactions'
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        super().__init__()

    def exec(self, data):
        """Get transactions from data object and print them to stdout.
        """
        self._logger.debug('running action with: %s', data)
        for transaction in data[self.TRANSACTIONS]:
            print(transaction)


class RemoveTransaction(Action):
    """Remove a transaction from db.
    """
    def __init__(self):
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        super().__init__()

    def exec(self, data):
        """Get transaction id from data and remove the
        corresponding transaction from db using TransactionManager.
        """
        self._logger.debug('running action with %s', data)
        transaction_manager = TransactionManager()
        transaction_manager.remove_transaction(data)


class UpdateTransaction(Action):
    """Update a transaction in db with new values.
    """

    def __init__(self):
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        super().__init__()

    def exec(self, data):
        """Get transaction from data and trigger update operation using
        TransactionManager.
        """
        self._logger.debug('running action with %s', data)
        transaction_manager = TransactionManager()
        try:
            transaction_manager.update_transaction(data['transaction'])
        except KeyError:
            raise ActionError('Missing input value: transaction')


class CreateStats(Action):
    """Process a set of transactions to generate statistics.
    """
    STATS = 'stats'
    STATS_TYPE = 'statstype'
    TRANSACTIONS = 'transactions'

    def __init__(self):
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        super().__init__()

    def exec(self, data):
        """Use stats helper to generate statistics.
        """
        self._logger.debug('running action with %s', data)
        stats_helper = StatsHelper(data[self.TRANSACTIONS])
        stats = stats_helper.create_stats(data[self.STATS_TYPE])
        data[self.STATS] = stats


class ShowStats(Action):
    """Show a set of stats.
    """
    DRAW = 'draw'
    STATS = 'stats'

    def __init__(self):
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        super().__init__()

    def exec(self, data):
        """Show a set of stats in in stdout.
        """
        self._logger.debug('running action with %s', data)
        if data[self.DRAW]:
            pass
        else:
            print(data[self.STATS])
