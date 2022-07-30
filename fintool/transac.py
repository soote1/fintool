"""
This module provides classes to create and manage transactions.
"""


import uuid
import datetime

from fintool.db import MissingCollectionError, DbFactory
from fintool.logging import LoggingHelper


class Error(Exception):
    """Base class for all errors in this module.
    """


class MissingFieldError(Error):
    """
    Raised when trying to convert a dictionary that misses a required field
    into a transaction.
    """


class InvalidFieldValueError(Error):
    """
    Raised when the user tries to assign an invalid value to some field.
    """


class InvalidTransactionError(Error):
    """
    Raised when the user passes an invalid transaction object to the
    transaction manager.
    """


class InvalidFieldError(Error):
    """
    Raised when the user requests a value for an invalid field.
    """


class Transaction:
    """
    A type to define a transaction object.
    """
    ID = 'id'
    TYPE = 'type'
    TAGS = 'tags'
    DATE = 'date'
    AMOUNT = 'amount'
    EMAIL_ID = 'email_id'
    SUPPORTED_TYPES = {'income', 'outcome'}

    def __init__(self, **kwargs):
        """Do input validation on arguments and initialize fields.

        Raise InvalidFieldValueError if argument is not expected or has
        invalid format.

        Args:
            id (str):         a guid
            type (str):       transaction type (income/outcome)
            tags (str):       a | separated list of words
            date (str):       a date with YYYY-MM-DD format
            amount (float):   a floating point number representing
                                the exchanged amount
            email_id (str):   an id generated by the email provider
        """
        try:
            if kwargs[self.TYPE] in self.SUPPORTED_TYPES:
                self.type = kwargs[self.TYPE]
            else:
                raise InvalidFieldValueError(
                    f'Invalid value {kwargs[self.TYPE]} for type'
                )

            try:
                self.tags = set(kwargs[self.TAGS].split('|'))
            except AttributeError:
                raise InvalidFieldValueError(
                    f'Invalid value {kwargs[self.TAGS]} for tags'
                )

            try:
                datetime.datetime.strptime(kwargs[self.DATE], '%Y-%m-%d')
                self.date = kwargs[self.DATE]
            except ValueError:
                raise InvalidFieldValueError(
                    f'Invalid value {kwargs[self.DATE]} for date'
                )

            try:
                self.amount = float(kwargs[self.AMOUNT])
            except ValueError:
                raise InvalidFieldValueError(
                    f"Invalid value {kwargs[self.AMOUNT]} for amount"
                )
        except KeyError as key_error:
            raise MissingFieldError(f'Missing required arg: {key_error}')

        self.id = kwargs[self.ID] if self.ID in kwargs else uuid.uuid4().hex
        self.email_id = kwargs.get(self.EMAIL_ID)

    def serialize(self):  # TODO: find a better method to generate this dict
        """
        Convert the transaction instance into a dictionary.
        """
        return {
            self.ID: self.id,
            self.TYPE: self.type,
            self.DATE: self.date,
            self.AMOUNT: self.amount,
            self.TAGS: '|'.join(self.tags),
            self.EMAIL_ID: self.email_id
        }

    def __str__(self):
        """
        Return a human-readable representation of the transaction instance.
        """
        return f'{self.id}\t{self.date}\t{self.type}\t{self.amount}'\
            f'\t{self.tags}\t{self.email_id}'


class TransactionManager:
    """
    A class to define the behavior of an object that knows how to manage
    transactions.
    """
    TRANSACTION_COLLECTION = 'records'

    def __init__(self, db=None):
        """
        Initialize instance.
        """
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        self._db = db if db else DbFactory.get_db('csv')()
        self._transaction_email_ids = set()

    def calculate_collection_from_date(self, date_str):
        """
        Return a string representing the namespace of the corresponding
        collection to fetch/store a transaction based in the given date. The
        namespace has the following pattern: YYYY/MM (2022/01)
        """
        self._logger.debug('calculating collection namespace for %s', date_str)
        date_parts = date_str.split('-')
        return f'{date_parts[0]}/{date_parts[1]}'

    def calculate_collections_from_date_range(self, from_str, to_str):
        """
        Return a list of strings representing the namespace of the
        corresponding collections to fetch/store transactions.
        """
        self._logger.debug(
            'calculating collection namespaces for range %s - %s',
            from_str,
            to_str
        )
        from_parts = from_str.split('-')
        to_parts = to_str.split('-')
        initial_year = int(from_parts[0])
        month = int(from_parts[1])
        year = initial_year
        year_limit = int(to_parts[0])
        month_limit = int(to_parts[1])
        collections = []

        while True:
            if month > month_limit and year == year_limit:  # stop the loop
                break
            elif month == 13:  # reset month and increase year
                month = 1
                year += 1
            else:  # calculate namespace for year and month
                date_str = f'{year}-{"0" if month < 10 else ""}{month}'
                collection = self.calculate_collection_from_date(date_str)
                collections.append(collection)
                month += 1

        return collections

    def create_transaction_list(self, dicts):
        """
        Create a list of Transaction instances from a list of dictionaries.
        """
        return [Transaction(**d) for d in dicts]

    def load_transaction_email_ids(self, collection):
        """
        Load transaction email ids into memory so that we can check for
        existence before inserting it.
        """
        txs = self.create_transaction_list(self._db.get_records(collection))
        self._transaction_email_ids.update([tx.email_id for tx in txs])

    def save_transaction(self, transaction):
        """Save a transaction in db.

        Args:
            transaction (Transaction): object to be saved in db
        """
        # TODO: need to get db type from cfg
        self._logger.debug('saving transaction in db')
        collection = self.calculate_collection_from_date(transaction.date)
        self.load_transaction_email_ids(collection)
        if transaction.email_id not in self._transaction_email_ids:
            self._db.add_record(
                record=transaction.serialize(),
                collection=collection
            )
        else:
            self._logger.debug('ignoring duplicate transaction')

    def filter_transactions(self, transactions, filters):
        """
        Filter a list of transaction based on a set of key-values
        """
        result = []
        # collect transactions matching any filter value only
        for transaction in transactions:
            for key, value in filters.items():
                try:
                    if key == Transaction.TAGS:
                        match = value & transaction.tags
                    else:
                        match = value == getattr(transaction, key)

                    if match:
                        result.append(transaction)
                        break
                except InvalidFieldError:
                    pass  # no problem, field doesn't exists

        return result

    def get_transactions(self, from_date, to_date, filters=None):
        """Get transactions from db and apply a set of filters.
        """
        self._logger.debug(
            'getting transactions from db using filters = %s', filters
        )
        collections = self.calculate_collections_from_date_range(
            from_date, to_date
        )
        records = []
        for collection in collections:
            try:
                records += self._db.get_records(collection)
            except MissingCollectionError:
                # no problem, log message and continue with next collection
                self._logger.debug('collection not found: %s', collection)

        transactions = self.create_transaction_list(records)

        if filters:
            transactions = self.filter_transactions(transactions, filters)

        return transactions

    def remove_transaction(self, date_str, guid_str):
        """Make sure that data contains a value for id field and use it
        to remove a transaction from db.
        """
        self._logger.debug('removing transaction %s', guid_str)
        collection = self.calculate_collection_from_date(date_str)
        self._db.remove_record(
            Transaction.ID,
            guid_str,
            collection
        )

    def check_need_to_move_record(self, old_date_str, new_date_str):
        """
        Check whether we need to move the record due to a change in the date
        associated date. We need to move the record if the year or month is
        different.
        """
        self._logger.debug('checking if record needs to be moved')
        old_date_parts = old_date_str.split('-')
        new_date_parts = new_date_str.split('-')
        return old_date_parts[0] != new_date_parts[0] or \
            old_date_parts[1] != new_date_parts[1]

    def update_transaction(self, old_date_str, data):
        """Update a transaction in db by using the provided id and data.
        """
        self._logger.debug('updating transaction %s with %s', data.id, data)
        if isinstance(data, Transaction):
            if self.check_need_to_move_record(old_date_str, data.date):
                self.remove_transaction(old_date_str, data.id)
                self.save_transaction(data)
            else:
                collection = self.calculate_collection_from_date(data.date)
                self._db.edit_record(
                    Transaction.ID,
                    data.id,
                    data.serialize(),
                    collection
                )
        else:
            raise InvalidTransactionError('invalid transaction object')
