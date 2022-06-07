"""
This module provides classes to create and manage transactions.
"""


import uuid
import datetime

from fintool.db import DbFactory
from fintool.logging import LoggingHelper


class Error(Exception):
    """Base class for all errors in this module.
    """


class MissingFieldError(Error):
    pass


class InvalidFieldValueError(Error):
    pass


class InvalidTransactionError(Error):
    pass


F_ID = 'id'
F_TYPE = 'type'
F_TAGS = 'tags'
F_DATE = 'date'
F_AMOUNT = 'amount'
SUPPORTED_TYPES = {'income', 'outcome'}


class Transaction:
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
        if t_type in SUPPORTED_TYPES:
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
            F_ID: self.id,
            F_TYPE: self.type,
            F_DATE: self.date,
            F_AMOUNT: self.amount,
            F_TAGS: self.tags
        }

    def serialize(self):
        return {
            F_ID: self.id,
            F_TYPE: self.type,
            F_DATE: self.date,
            F_AMOUNT: self.amount,
            F_TAGS: '|'.join(self.tags)
        }

    def has_field(self, field):
        return field in self._fields

    def get_value(self, field):
        return self._fields[field]

    def __repr__(self):
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

    def create_transaction(self, data):
        """Create a transaction from a dictionary instance.

        Args:
            data (dict): A dictionary with values for new transaction.
        """
        self._logger.debug('creating new transaction with %s', data)

        try:
            transaction = Transaction(
                data[F_TYPE],
                data[F_TAGS],
                data[F_DATE],
                data[F_AMOUNT],
                data[F_ID] if F_ID in data else None
            )
        except KeyError as key_error:
            raise MissingFieldError(key_error)

        # keep id if was provided in data
        if F_ID in data:
            transaction.id = data[F_ID]

        return transaction

    def create_transaction_list(self, dicts):
        """
        Create a list of Transaction instances from a list of dictionaries.
        """
        return [self.create_transaction(d) for d in dicts]

    def save_transaction(self, transaction):
        """Save a transaction in db.

        Args:
            transaction (Transaction): object to be saved in db
        """
        # TODO: need to get db type from cfg
        # TODO: need to inject db object so that we can test with mock data
        self._logger.debug('saving transaction in db')
        self._db.add_record(
            record=transaction.serialize(),
            collection=self.TRANSACTION_COLLECTION
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
                    match = value & transaction.tags if key == F_TAGS \
                            else value == transaction.get_value(key)

                    if match:
                        result.append(transaction)
                        break
                except KeyError:
                    pass  # no problem, field doesn't exists

        return result

    def get_transactions(self, filters=None):
        """Get transactions from db and apply a set of filters.
        """
        self._logger.debug(
            'getting transactions from db using filters = %s', filters
        )
        records = self._db.get_records(self.TRANSACTION_COLLECTION)
        transactions = self.create_transaction_list(records)

        if filters:
            transactions = self.filter_transactions(transactions, filters)

        return transactions

    def remove_transaction(self, data):
        """Make sure that data contains a value for id field and use it
        to remove a transaction from db.
        """
        try:
            id_value = data[F_ID]
        except KeyError:
            raise MissingFieldError(f'missing field {F_ID}')

        self._logger.debug('removing transaction %s', id_value)
        self._db.remove_record(F_ID, id_value, self.TRANSACTION_COLLECTION)

    def update_transaction(self, data):
        """Update a transaction in db by using the provided id and data.
        """
        self._logger.debug('updating transaction %s with %s', data.id, data)
        if isinstance(data, Transaction):
            self._db.edit_record(
                F_ID,
                data.id,
                data.serialize(),
                self.TRANSACTION_COLLECTION
            )
        else:
            raise InvalidTransactionError('invalid transaction object')
