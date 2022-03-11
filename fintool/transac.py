"""
This module provides clases to create and manage transactions.
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
    @classmethod
    def create_transaction(cls, data):
        """Create a transaction from a dictionary instance.

        Args:
            data (dict): A dictionary with values for new transaction.
        """
        LoggingHelper.get_logger(cls.__name__).debug(
            'creating new transaction with %s',
            data
        )

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

    @classmethod
    def create_transaction_list(cls, dicts):
        return [cls.create_transaction(current_dict) for current_dict in dicts]

    @classmethod
    def save_transaction(cls, transaction):
        """Save a transaction in db.

        Args:
            transaction (Transaction): object to be saved in db
        """
        # TODO: need to get db type from cfg
        # TODO: need to inject db object so that we can test with mock data
        LoggingHelper.get_logger(cls.__name__).debug(
            'saving transaction in db'
        )
        fintool_db = DbFactory.get_db('csv')()
        fintool_db.add_record(record=transaction.serialize())

    @classmethod
    def filter_transactions(cls, transactions, filters):
        """Filter a list of transaction based on a set of key-values
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

    @classmethod
    def get_transactions(cls, filters=None):
        """Get transactions from db and apply a set of filters.
        """
        LoggingHelper.get_logger(cls.__name__).debug(
            'getting transactions from db using filters = %s', filters
        )
        fintool_db = DbFactory.get_db('csv')()
        transactions = cls.create_transaction_list(fintool_db.get_records())

        if filters:
            transactions = cls.filter_transactions(transactions, filters)

        return transactions

    @classmethod
    def remove_transaction(cls, data):
        """Make sure that data contains a value for id field and use it
        to remove a transaction from db.
        """
        try:
            id_value = data[F_ID]
        except KeyError:
            raise MissingFieldError(f'missing field {F_ID}')

        LoggingHelper.get_logger(cls.__name__).debug(
            'removing transaction %s', id_value
        )
        fintool_db = DbFactory.get_db('csv')()
        fintool_db.remove_record(F_ID, id_value)

    @classmethod
    def update_transaction(cls, data):
        """Update a transaction in db by using the provided id and data.
        """
        if isinstance(data, Transaction):
            LoggingHelper.get_logger(cls.__name__).debug(
                'updating transaction %s with %s', data.id, data
            )
            fintool_db = DbFactory.get_db('csv')()
            fintool_db.edit_record(F_ID, data.id, data.serialize())
        else:
            raise InvalidTransactionError('invalid transaction object')


class StatsHelper:
    """Generate different types of stats based on a list of transactions
    """

    def __init__(self):
        pass

    @classmethod
    def create_summary(cls):
        pass
