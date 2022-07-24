"""
This module provides mechanisms to synchronize transactions. That is, to fetch
transactions from a specific email service provider and insert them into the
local db.
"""
import time

from fintool.db import DbFactory, MissingCollectionError
from fintool.logging import LoggingHelper
from fintool.tagging import TagManager, NoTagsError
from fintool.email import (
    build_client,
    build_parser,
    MissingFieldError,
    TransactionEmail
)
from fintool.transac import Transaction, TransactionManager


class Error(Exception):
    """
    Base class for errors in this module.
    """


class MissingRequiredFieldError(Error):
    """
    Raised when some data object is missing a required field.
    """


class InvalidInputObject(Error):
    """
    Raised when the input object for some process has invalid structure.
    """


class SyncDetails:
    """
    A type to define the synchronization details for the sync manager.
    """
    def __init__(self, provider, email_type, mail_boxes, start_date):
        """
        Initialize instance.
        """
        self.provider = provider
        self.mail_boxes = mail_boxes
        self.email_type = email_type
        self.start_date = start_date


class TaggingResult:
    """
    A class to define the result of the tagging process.
    """
    def __init__(self, tagged, untagged):
        """
        Initialize instance.
        """
        self.tagged = tagged
        self.untagged = untagged


class TaggedTransaction:
    """
    A class to define a tagged transaction.
    """
    def __init__(self, **kwargs):
        self.tags = kwargs.get('tags')
        self.concept = kwargs.get('concept')
        self.email_id = kwargs.get('email_id')
        self.date = kwargs.get('date')
        self.amount = kwargs.get('amount')

    def serialize(self):
        """
        Convert instance into a dictionary.
        """
        return {
            'tags': self.tags,
            'concpet': self.concept,
            'email_id': self.email_id,
            'date': self.date,
            'amount': self.amount
        }


class LastSync:
    """
    A class to represent the last sync date.
    """
    LAST_SYNC = 'last_sync'

    def __init__(self, last_sync):
        """
        Initialize instance.
        """
        self.last_sync = last_sync

    def serialize(self):
        """
        Convert instance into a dictionary.
        """
        return {self.LAST_SYNC: self.last_sync}

    @staticmethod
    def from_dict(d):
        """
        Create a LastSync instance from a given dictionary.
        """
        try:
            return LastSync(int(d[LastSync.LAST_SYNC]))
        except KeyError as e:
            raise MissingRequiredFieldError(
                f"Missing {e} key"
            )


class SyncManager:
    """
    A class that knows how to synchronize emails.
    """
    SYNC_COLLECTION = 'sync'
    UNTAGGED_COLLECTION = 'untagged'
    LAST_SYNC = 'lastsync'

    def __init__(self):
        """
        Initialize instance.
        """
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        self._tag_manager = TagManager()
        self._transaction_manager = TransactionManager()
        self._db = DbFactory.get_db('csv')()

    def create_transaction_from_transaction_email(self, transaction_email):
        """
        Build a transaction instance using the given tags and the given
        transaction email.
        """
        return Transaction(
            'income',
            transaction_email.tags,
            transaction_email.date,
            transaction_email.amount
        )

    def create_transaction_list_from_transaction_emails(
        self,
        transaction_emails
    ):
        """
        Create a list of Transaction instances from a list of parsed emails.
        """
        return [
            self.create_transaction_from_transaction_email(transaction_email)
            for transaction_email in transaction_emails
        ]

    def sync_transactions(self, sync_details):
        """
        Fetch the transaction emails using the given sync_details, tag the
        transactions and store them in the corresponding collection.
        """
        try:
            last_sync = self.get_last_sync(self.LAST_SYNC)
            last_sync = last_sync.last_sync + 1 if last_sync else 0
        except MissingCollectionError:
            last_sync = None  # the collection doesn't exists in first run

        transaction_emails = self.fetch_transaction_emails(
            sync_details.provider,
            sync_details.email_type,
            sync_details.mail_boxes,
            last_sync
        )
        # we might need to decrease this to catch missing emails in next sync
        # or maybe we just need to calculate this value before fetch
        if not last_sync:
            last_sync = int(time.time())
        try:
            tagging_result = self.tag_transaction_emails(transaction_emails)
            self.save_transaction_emails(
                tagging_result.tagged,
                self.SYNC_COLLECTION
            )
            self.save_transaction_emails(
                tagging_result.untagged,
                self.UNTAGGED_COLLECTION
            )
        except NoTagsError:
            self._logger.debug('No tags available in db')
            # mark transactions as untaged
            self.save_transaction_emails(
                transaction_emails,
                self.UNTAGGED_COLLECTION
            )

        self.update_last_sync(last_sync, self.LAST_SYNC)

    def tag_transaction_emails(self, transaction_emails):
        """
        Process a list of transactions to add the corresponding set of tags to
        them. The transaction concept is used as the key for searching the
        tags.
        """
        untagged = []
        tagged = []
        for transaction_email in transaction_emails:
            tags = self._tag_manager.match_concpet(transaction_email.concept)
            if tags:
                transaction_email.tags = tags
                tagged.append(transaction_email)
            else:
                untagged.append(transaction_email)

        return TaggingResult(tagged, untagged)

    def fetch_transaction_emails(
            self,
            provider,
            email_type,
            mail_boxes,
            from_date
    ):
        """
        Fetch transactions from an email service provider.
        """
        transaction_emails = []
        email_client = build_client(provider)
        email_parser = build_parser(email_type)
        emails = email_client.fetch_emails(mail_boxes, from_date)
        for email in emails:
            try:
                transaction_emails.append(email_parser.parse_email(email))
            except MissingFieldError:
                continue  # TODO: think if we should do something with error
        return transaction_emails

    def save_transactions(self, transactions):
        """
        Process a list of transactions to store them in a db collection.
        """
        for transaction in transactions:
            self.save_transaction(transaction)

    def save_transaction(self, transaction):
        """
        Save a given transaction in db.
        """
        self._transaction_manager.save_transaction(transaction)

    def save_transaction_emails(self, transaction_emails, collection):
        """
        Process a list of transaction emails to persist them in the given
        collection.
        """
        for transaction_email in transaction_emails:
            self.save_transaction_email(transaction_email, collection)

    def save_transaction_email(self, transaction_email, collection):
        """
        Persist a transaction email in the given collection.
        """
        self._db.add_record(transaction_email.serialize(), collection)

    def get_last_sync(self, collection):
        """
        Get last sync from db.
        """
        self._logger.debug('Reading last sync from db')
        result = self._db.get_records(collection)
        if result:
            try:
                return LastSync.from_dict(result[0])
            except MissingFieldError as e:
                raise InvalidInputObject(
                    f"Can't create Lastsync instance: {e}"
                )

        return None

    def remove_last_sync(self, collection):
        """
        Remove last sync from db.
        """
        self._logger.debug("Removing last sync from db")
        last_sync = self.get_last_sync(collection)
        if last_sync:
            self._db.remove_record(
                LastSync.LAST_SYNC,
                str(last_sync.last_sync),  # db compares this against a string
                collection
            )

    def save_last_sync(self, last_sync, collection):
        """
        Save last sync in db.
        """
        self._logger.debug("Saving last sync in db")
        self._db.add_record(LastSync(last_sync).serialize(), collection)

    def update_last_sync(self, last_sync, collection):
        """
        Update the value of last sync in the db.
        """
        self._logger.debug("Updating last sync in db")
        try:
            self.remove_last_sync(collection)
        except MissingCollectionError:
            pass  # the collection doesn't exists the first time

        self.save_last_sync(last_sync, collection)

    def load_untagged_transactions(self):
        """
        Load untagged transactions from db and return a list of
        TransactionEmail instances.
        """
        records = self._db.get_records(self.UNTAGGED_COLLECTION)
        transaction_emails = []
        for record in records:
            transaction_emails.append(TransactionEmail.from_dict(record))

        return transaction_emails

    def create_concepts_set(self):
        """
        Process a list of TransactionEmail instances to generate a unique
        set of concepts.
        """
        concepts_set = set()
        transaction_emails = self.load_untagged_transactions()

        for transaction_email in transaction_emails:
            concepts_set.add(transaction_email.concept)

        return concepts_set

    def load_sync_transactions(self):
        """
        Load sync transactions from db and return a list.
        """
        records = self._db.get_records(self.SYNC_COLLECTION)
        pending_transactions = []
        for record in records:
            pending_transactions.append(TaggedTransaction(**record))

        return pending_transactions
