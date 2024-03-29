"""
This module provides mechanisms to synchronize transactions. That is, to fetch
transactions from a specific email service provider and insert them into the
local db.
"""
import time

from fintool.db import DbFactory, MissingCollectionError
from fintool.log import LoggingHelper
from fintool.tagging import TagManager, NoTagsError
from fintool.email import (
    build_client,
    build_parser,
    MissingFieldError,
    TransactionEmail
)
from fintool.transac import Transaction, TransactionManager
from fintool.errors import Error


class SyncError(Error):
    """Type to identify errors related to this module."""
    def __init__(self, msg):
        super().__init__(f'Sync error: {msg}')


class MissingRequiredFieldError(SyncError):
    """
    Raised when some data object is missing a required field.
    """


class InvalidInputObject(SyncError):
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
    TAGS = 'tags'
    CONCEPT = 'concept'
    EMAIL_ID = 'email_id'
    DATE = 'date'
    AMOUNT = 'amount'

    def __init__(self, **kwargs):
        self.tags = kwargs.get(self.TAGS)
        self.concept = kwargs.get(self.CONCEPT)
        self.email_id = kwargs.get(self.EMAIL_ID)
        self.date = kwargs.get(self.DATE)
        self.amount = kwargs.get(self.AMOUNT)

    def serialize(self):
        """
        Convert instance into a dictionary.
        """
        return {
            self.TAGS: self.tags,
            self.CONCEPT: self.concept,
            self.EMAIL_ID: self.email_id,
            self.DATE: self.date,
            self.AMOUNT: self.amount
        }


class LastSync:
    """
    A class to represent the last sync date.
    """
    LAST_SYNC = 'last_sync'
    TARGET = 'target'

    def __init__(self, last_sync=None, target=None):
        """
        Initialize instance.
        """
        self.last_sync = int(last_sync)
        self.target = target

    def serialize(self):
        """
        Convert instance into a dictionary.
        """
        return {
            self.LAST_SYNC: self.last_sync,
            self.TARGET: self.target
        }


class SyncManager:
    """
    A class that knows how to synchronize emails.
    """
    PENDING_COLLECTION = 'pending'
    UNTAGGED_COLLECTION = 'untagged'
    LAST_SYNC = 'lastsync'

    def __init__(self, db=None):
        """
        Initialize instance.
        """
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        self._tag_manager = TagManager()
        self._transaction_manager = TransactionManager()
        self._db = db if db else DbFactory.get_db('csv')()

    def create_transaction_from_transaction_email(self, transaction_email):
        """
        Build a transaction instance using the given tags and the given
        transaction email.
        """
        return Transaction(
            type='outcome',
            tags=transaction_email.tags,
            date=transaction_email.date,
            amount=transaction_email.amount
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
            last_sync = self.get_last_sync(
                sync_details.provider,
                sync_details.email_type,
                sync_details.mail_boxes,
                self.LAST_SYNC
            )
        except MissingCollectionError:
            last_sync = None  # the collection doesn't exists in first run

        transaction_emails = self.fetch_transaction_emails(
            sync_details.provider,
            sync_details.email_type,
            sync_details.mail_boxes,
            last_sync.last_sync if last_sync else last_sync
        )
        last_sync = int(time.time())  # calculate timestamp for next sync
        try:
            tagging_result = self.tag_transaction_emails(transaction_emails)
            self.save_transaction_emails(
                tagging_result.tagged,
                self.PENDING_COLLECTION
            )
            self.save_transaction_emails(
                tagging_result.untagged,
                self.UNTAGGED_COLLECTION
            )
        except NoTagsError:
            self._logger.debug('No tags available in db')
            # mark transactions as untagged
            self.save_transaction_emails(
                transaction_emails,
                self.UNTAGGED_COLLECTION
            )

        self.update_last_sync(
            sync_details.provider,
            sync_details.email_type,
            sync_details.mail_boxes,
            last_sync, self.LAST_SYNC
        )

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
                transaction_email = email_parser.parse_email(email)
                transaction_emails.append(transaction_email)
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

    def get_last_sync(self, provider, email_type, mail_boxes, collection):
        """
        Get last sync from db.
        """
        self._logger.debug('Reading last sync from db')
        target = f'{provider},{email_type},{mail_boxes}'
        records = self._db.get_records(collection)
        for record in records:
            try:
                last_sync = LastSync(**record)
                if last_sync.target == target:
                    return last_sync
            except MissingFieldError as e:
                raise InvalidInputObject(
                    f"Can't create Lastsync instance: {e}"
                )

        return None

    def remove_last_sync(self, provider, email_type, mail_boxes, collection):
        """
        Remove last sync from db.
        """
        self._logger.debug("Removing last sync from db")
        last_sync = self.get_last_sync(provider, email_type, mail_boxes, collection)
        if last_sync:
            self._db.remove_record(
                LastSync.LAST_SYNC,
                str(last_sync.last_sync),  # db compares this against a string
                collection
            )

    def save_last_sync(self, provider, email_type, mail_boxes, last_sync_timestamp, collection):
        """
        Save last sync in db.
        """
        self._logger.debug("Saving last sync in db")
        last_sync = LastSync(
            last_sync=last_sync_timestamp,
            target=f'{provider},{email_type},{mail_boxes}'
        )
        self._db.add_record(last_sync.serialize(), collection)

    def update_last_sync(self, provider, email_type, mail_boxes, last_sync_timestamp, collection):
        """
        Update the value of last sync in the db.
        """
        self._logger.debug("Updating last sync in db")
        try:
            self.remove_last_sync(provider, email_type, mail_boxes, collection)
        except MissingCollectionError:
            pass  # the collection doesn't exists the first time

        self.save_last_sync(provider, email_type, mail_boxes, last_sync_timestamp, collection)

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

    def load_pending_transactions(self):
        """
        Load pending transactions from db and return a list.
        """
        records = self._db.get_records(self.PENDING_COLLECTION)
        pending_transactions = []
        for record in records:
            pending_transactions.append(TaggedTransaction(**record))

        return pending_transactions

    def commit_transactions(self):  # TODO: take care of duplicates
        """Move transactions from sync db to transactions db. Reset sync after
        committing transactions.
        """
        transaction_manager = TransactionManager()
        for tagged_transaction in self.load_pending_transactions():
            transaction = Transaction(
                type='outcome',
                tags=tagged_transaction.tags,
                date=tagged_transaction.date,
                amount=tagged_transaction.amount,
                email_id=tagged_transaction.email_id
            )
            transaction_manager.save_transaction(transaction)
        self._db.remove_collection(self.PENDING_COLLECTION)

    def tag_transactions(self):
        """
        Try to tag transactions from untagged db and save them in sync db.
        """
        untagged_transactions = self.load_untagged_transactions()
        tagging_result = self.tag_transaction_emails(untagged_transactions)
        self.save_transaction_emails(
            tagging_result.tagged,
            self.PENDING_COLLECTION
        )
        self._db.remove_collection(self.UNTAGGED_COLLECTION)
        self.save_transaction_emails(
            tagging_result.untagged,
            self.UNTAGGED_COLLECTION
        )
