"""
This module provides action classes that can be put into a sequence
to create commands for cli object.
"""


from fintool.transac import Transaction, TransactionManager
from fintool.logging import LoggingHelper
from fintool.stats import StatsHelper
from fintool.tagging import Tag, TagManager
from fintool.sync import SyncManager, SyncDetails


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
        self.FROM = 'from'
        self.TO = 'to'
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        super().__init__()

    def exec(self, data):
        """Use TransactionManager to get transactions from db.
        """
        self._logger.debug('running action with: %s', data)
        transaction_manager = TransactionManager()
        txs = transaction_manager.get_transactions(
            data[self.FROM],
            data[self.TO],
            filters=data[self.FILTERS]
        )
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
        self.ID = 'id'
        self.DATE = 'date'
        super().__init__()

    def exec(self, data):
        """Get transaction id from data and remove the
        corresponding transaction from db using TransactionManager.
        """
        self._logger.debug('running action with %s', data)
        transaction_manager = TransactionManager()
        transaction_manager.remove_transaction(data[self.DATE], data[self.ID])


class UpdateTransaction(Action):
    """Update a transaction in db with new values.
    """

    def __init__(self):
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        self.OLD_DATE = 'olddate'
        self.TRANSACTION = 'transaction'
        super().__init__()

    def exec(self, data):
        """Get transaction from data and trigger update operation using
        TransactionManager.
        """
        self._logger.debug('running action with %s', data)
        transaction_manager = TransactionManager()
        try:
            transaction_manager.update_transaction(
                data[self.OLD_DATE],
                data[self.TRANSACTION]
            )
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


class CreateTag(Action):
    """
    Create a Tag instance from command data.
    """
    CONCEPT = 'concept'
    TAGS = 'tags'
    TAG_ID = 'tagid'
    TAG = 'tag'

    def __init__(self):
        """
        Initialize instance.
        """
        self._logger = LoggingHelper().get_logger(self.__class__.__name__)
        super().__init__()

    def exec(self, data):
        """
        Read cli arguments from data, create a Tag instance and
        add it to data.
        """
        self._logger.debug('running action with %', data)
        try:
            concept = data[self.CONCEPT]
            tags = data[self.TAGS]
            tag_id = data.get(self.TAG_ID, None)
        except KeyError as e:
            raise ActionError(f'Missing required input element: {e}')

        tag = Tag(concept=concept, tags_str=tags, tag_id=tag_id)
        data[self.TAG] = tag


class AddTag(Action):
    """
    Insert a tag into the db.
    """
    TAG = 'tag'

    def __init__(self):
        """
        Initialize instance.
        """
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        super().__init__()

    def exec(self, data):
        """
        Insert a Tag instance into the db using the tag manager.
        """
        self._logger.debug('running action with: %s', data)
        try:
            tag = data[self.TAG]
        except KeyError as e:
            raise ActionError(f'Missing required input element: {e}')

        tag_manager = TagManager()
        tag_manager.add_tag(tag)


class GetTags(Action):
    """
    Retrieve all tags from db.
    """
    TAGS = 'tags'

    def __init__(self):
        """
        Initialize instance.
        """
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        super().__init__()

    def exec(self, data):
        """
        Retrieve all the tags from the db using the TagManager.
        """
        self._logger.debug('running action with: %s', data)
        tag_manager = TagManager()
        tags = tag_manager.get_tags()
        data[self.TAGS] = tags


class EditTag(Action):
    """
    Change the values of an existing tag.
    """
    TAG = 'tag'

    def __init__(self):
        """
        Initialize instance.
        """
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        super().__init__()

    def exec(self, data):
        """
        Replace the existing values of a given tag with the new values
        provided as cli arguments.
        """
        self._logger.debug('running action with: %s', data)
        try:
            tag = data[self.TAG]
        except KeyError as e:
            raise ActionError(f'Missing required input element: {e}')
        tag_manager = TagManager()
        tag_manager.update_tag(tag)


class RemoveTag(Action):
    """
    Remove a tag from the db.
    """
    TAG_ID = 'tagid'

    def __init__(self):
        """
        Initialize instance.
        """
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        super().__init__()

    def exec(self, data):
        """
        Remove a tag from the db using the given id.
        """
        self._logger.debug('running action with: %s', data)
        try:
            tag_id = data[self.TAG_ID]
        except KeyError as e:
            raise ActionError(f'Missing required input element: {e}')

        tag_manager = TagManager()
        tag_manager.delete_tag(tag_id)


class PrintTags(Action):
    """
    Print a list of tags to stdout.
    """
    TAGS = 'tags'

    def __init__(self):
        """
        Initialize instance.
        """
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        super().__init__()

    def exec(self, data):
        """
        Print a list of tags to stdout.
        """
        for tag in data[self.TAGS]:
            print(tag)


class SyncController(Action):
    """An action to perform sync operations."""

    def __init__(self):
        """Initialize instance."""

    def exec(self, data):
        """Run corresponding action based in provided cli args."""

        if 'show' in data:
            pass
        elif 'untagged' in data:
            pass
        elif 'commit' in data:
            pass
        else:
            action = SyncTransactions()

        action.exec(data)


class SyncTransactions(Action):
    """
    An action to download transactions from an email provider.
    """
    def __init__(self):
        """
        Initialize instance.
        """
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        super().__init__()

    def exec(self, data):
        """
        Download transactions from an email provider using the sync manager.
        """
        try:
            bank = data['bank']
            mail_box = data['mailbox']
            provider = data['provider']
        except KeyError as e:
            raise ActionError(f'Missing required input element: {e}')

        sync_manager = SyncManager()
        sync_details = SyncDetails(provider, bank, mail_box, '')
        sync_manager.sync_transactions(sync_details)
