"""
This module provides action classes that can be put into a sequence
to create commands for cli object.
"""
import abc

from fintool.transac import Transaction, TransactionManager
from fintool.log import LoggingHelper
from fintool.stats import StatsHelper
from fintool.tagging import Tag, TagManager
from fintool.sync import SyncManager, SyncDetails
from fintool.charts import ChartFactory
from fintool.config import ConfigManager
from fintool.errors import Error


class ActionError(Error):
    """Type to identify errors from this module"""
    def __init__(self, msg):
        super().__init__(f'Action error: {msg}')


class Action(abc.ABC):
    """Base type to represent actions."""
    def __init__(self, action_name):
        self._logger = LoggingHelper.get_logger(action_name)
        super().__init__()

    @abc.abstractmethod
    def exec(self, data):
        """Must be implemented by concrete classes."""
        pass


class CreateTransaction(Action):
    """Create a Transaction instance from command data.
    """

    def __init__(self):
        super().__init__(self.__class__.__name__)

    def exec(self, data):
        """Create a Transaction object and insert it into data.

        Args:
            data (dict): A dictionary containing required key-values to create
                            a transaction.
        """
        self._logger.debug('running action with: %s', data)
        try:
            data["transaction"] = Transaction(**data)
        except Exception as exception:
            raise ActionError(exception)


class SaveTransaction(Action):
    """Save a transaction in fintool db.
    """

    def __init__(self):
        super().__init__(self.__class__.__name__)

    def exec(self, data):
        """Retrieve a transaction from data, serialize it and save it in
        fintool db.

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
        super().__init__(self.__class__.__name__)

    def exec(self, data):
        """Create a dictionary with filters from cli options.
        """
        self._logger.debug('running action with: %s', data)
        filters = {}
        if data['txtype']:
            filters[self.TYPE] = data['txtype']

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
        super().__init__(self.__class__.__name__)

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
        super().__init__(self.__class__.__name__)

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
        self.ID = 'id'
        self.DATE = 'date'
        super().__init__(self.__class__.__name__)

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
        self.OLD_DATE = 'olddate'
        self.TRANSACTION = 'transaction'
        super().__init__(self.__class__.__name__)

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
    STATS_TYPE = 'sttype'
    TRANSACTIONS = 'transactions'

    def __init__(self):
        super().__init__(self.__class__.__name__)

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
    DRAW_ONLY = 'draw_only'

    def __init__(self):
        super().__init__(self.__class__.__name__)

    def exec(self, data):
        """Show a set of stats in in stdout.
        """
        self._logger.debug('running action with %s', data)
        chart_type = data[self.DRAW]
        stats = data[self.STATS]

        draw_only = data.get(self.DRAW_ONLY, [])
        if draw_only:
            draw_only = draw_only.split('|')

        if chart_type:
            chart_data = stats.get_chart_data()
            chart = ChartFactory.build_chart(chart_type)

            # TODO: refactor this block so it is in a different place
            # filter target tags
            if draw_only:
                tags_to_draw = {}
                for tag in draw_only:
                    tags_to_draw[tag] = chart_data['y_values'][tag]
                chart_data['y_values'] = tags_to_draw

            # TODO: refactor this block so it is in a different place
            if chart_type == 'pie':
                labels = []
                section_values = []
                for label, values in chart_data['y_values'].items():
                    labels.append(label)
                    section_values.append(values[0])
                chart_data['labels'] = labels
                chart_data['y_values'] = section_values

            chart.draw(
                chart_data['title'],
                chart_data['ylabel'],
                chart_data['labels'],
                chart_data['y_values']
            )
        else:
            print(stats)


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
        super().__init__(self.__class__.__name__)

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
        super().__init__(self.__class__.__name__)

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
        super().__init__(self.__class__.__name__)

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
        super().__init__(self.__class__.__name__)

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
        super().__init__(self.__class__.__name__)

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
        super().__init__(self.__class__.__name__)

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
        super().__init__(self.__class__.__name__)

    def exec(self, data):
        """Run corresponding action based in provided cli args."""

        if data['pending']:
            action = ShowPendingTransactions()
        elif data['untagged']:
            action = ShowUntaggedTransactions()
        elif data['concepts']:
            action = ShowConcepts()
        elif data['commit']:
            action = CommitTransactions()
        elif data['tag']:
            action = TagTransactions()
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
        super().__init__(self.__class__.__name__)

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


class ShowPendingTransactions(Action):
    """An action to show the contents of the pending db."""
    def __init__(self):
        """
        Initialize instance.
        """
        super().__init__(self.__class__.__name__)

    def exec(self, data):
        """Load the contents of the pending db and print them in stdout."""
        sync_manager = SyncManager()
        pending_transactions = sync_manager.load_pending_transactions()
        for t in pending_transactions:
            print(t.serialize())


class ShowUntaggedTransactions(Action):
    """An action to show the contents of the untagged db."""
    def __init__(self):
        """
        Initialize instance.
        """
        super().__init__(self.__class__.__name__)

    def exec(self, data):
        """Load the contents of the untagged db and print them in stdout."""
        sync_manager = SyncManager()
        untagged_transactions = sync_manager.load_untagged_transactions()
        for t in untagged_transactions:
            print(t.serialize())


class ShowConcepts(Action):
    """An action to show the concepts from untagged transactions."""
    def __init__(self):
        """
        Initialize instance.
        """
        super().__init__(self.__class__.__name__)

    def exec(self, data):
        """Load the contents from untagged transactions db, generate the unique
        set of concepts and print them in stdout.
        """
        sync_manager = SyncManager()
        concepts_set = sync_manager.create_concepts_set()
        for concept in concepts_set:
            print(concept)


class CommitTransactions(Action):
    """An action to move transactions from sync db to main db."""
    def __init__(self):
        """
        Initialize instance.
        """
        super().__init__(self.__class__.__name__)

    def exec(self, data):
        """Use the sync manager to commit tagged transactions.
        """
        sync_manager = SyncManager()
        sync_manager.commit_transactions()


class TagTransactions(Action):
    """An action to tag untagged transactions and store them in sync db.
    """
    def __init__(self):
        """Initialize instance."""
        super().__init__(self.__class__.__name__)

    def exec(self, data):
        """Use the sync manager to tag transactions from untagged db."""
        sync_manager = SyncManager()
        sync_manager.tag_transactions()


class ShowSetting(Action):
    """
    An action to print the value of a setting in the stdout.
    """
    def __init__(self):
        """Initialize instance."""
        super().__init__(self.__class__.__name__)

    def exec(self, data):
        """
        Get the corresponding value for the given setting and print it in
        stdout.
        """
        setting = data['setting']
        value = ConfigManager.get(setting)
        print(value)


class SetSetting(Action):
    """
    An action to create/update a setting.
    """
    def __init__(self):
        """Initialize instance."""
        super().__init__(self.__class__.__name__)

    def exec(self, data):
        """
        Use the config manager to update an existing setting or create it. If
        the --append option was passed, then add the new value to the existing
        one instead of replacing it.
        """
        key = data['setting']
        value = data['value']
        append = data['append']

        if append:
            ConfigManager.append(key, value)
        else:
            ConfigManager.set(key, value)

        ConfigManager.dump_config()
