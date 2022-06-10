"""
This module provides classes to create and manage transactions.
"""


import uuid
import datetime

from fintool.db import CollectionNotFoundError, DbFactory
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
    SUPPORTED_TYPES = {'income', 'outcome'}
    def __init__(self, t_type, t_tags, t_date, t_amount, t_id=None):
        """Do input validation on arguments and initialize fields.

        Raise InvalidFieldValueError if argument is not expected or has
        invalid format.

        Args:
            t_id (str):         a guid
            t_type (str):       transaction type (income/outcome)
            t_tags (str):       a | separated list of words
            t_date (str):       a date with YYYY-MM-DD format
            t_amount (float):   a floating point number representing
                                the exchanged amount
        """
        if t_type in self.SUPPORTED_TYPES:
            self.type = t_type
        else:
            raise InvalidFieldValueError(
                f'Invalid value {t_type} for transaction type'
            )

        try:
            self.tags = set(t_tags.split('|'))
        except AttributeError:
            raise InvalidFieldValueError(
                f'Invalid value {t_tags} for transaction tags'
            )

        try:
            datetime.datetime.strptime(t_date, '%Y-%m-%d')
            self.date = t_date
        except ValueError:
            raise InvalidFieldValueError(
                f'Invalid value {t_date} for transaction date'
            )

        try:
            self.amount = float(t_amount)
        except ValueError:
            raise InvalidFieldValueError(
                f"Invalid value {t_amount} for transaction amount"
            )

        self.id = t_id if t_id else uuid.uuid4().hex

        self._fields = {
            self.ID: self.id,
            self.TYPE: self.type,
            self.DATE: self.date,
            self.AMOUNT: self.amount,
            self.TAGS: self.tags
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create a transaction instance from a dict object.
        """
        try:
            transaction = Transaction(
                data[cls.TYPE],
                data[cls.TAGS],
                data[cls.DATE],
                data[cls.AMOUNT],
                data[cls.ID] if cls.ID in data else None
            )
        except KeyError as key_error:
            raise MissingFieldError(f'Input dict is missing: {key_error}')

        # keep id if was provided in data
        if cls.ID in data:
            transaction.id = data[cls.ID]

        return transaction

    def serialize(self):
        """
        Convert the transaction instance into a dictionary.
        """
        return {
            self.ID: self.id,
            self.TYPE: self.type,
            self.DATE: self.date,
            self.AMOUNT: self.amount,
            self.TAGS: '|'.join(self.tags)
        }

    def get_value(self, field):
        """
        Return the corresponding value for the given key.
        """
        try:
            return self._fields[field]
        except KeyError:
            raise InvalidFieldError(f'{field} is not supported')

    def __str__(self):
        """
        Return a human-readable representation of the transaction instance.
        """
        return f'{self.id}\t{self.date}\t{self.type}\t{self.amount}'\
            f'\t{self.tags}'


class TransactionManager:
    """
    A class to define the behavior of an object that knows how to manage
    transactions.
    """
    TRANSACTION_COLLECTION = 'records'

    def __init__(self):
        """
        Initialize instance.
        """
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        self._db = DbFactory.get_db('csv')()

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
        return [Transaction.from_dict(d) for d in dicts]

    def save_transaction(self, transaction):
        """Save a transaction in db.

        Args:
            transaction (Transaction): object to be saved in db
        """
        # TODO: need to get db type from cfg
        # TODO: need to inject db object so that we can test with mock data
        self._logger.debug('saving transaction in db')
        collection = self.calculate_collection_from_date(transaction.date)
        self._db.add_record(
            record=transaction.serialize(),
            collection=collection
        )

    def filter_transactions(self, transactions, filters):
        """
        Filter a list of transaction based on a set of key-values
        """
        result = []
        # collect transactions matching any filter value only
        for transaction in transactions:
            for key, value in filters.items():
                try:
                    match = value & transaction.tags if key == Transaction.TAGS \
                            else value == transaction.get_value(key)

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
            except CollectionNotFoundError:
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
