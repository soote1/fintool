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
    pass


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
    def __init__(self, t_type, t_tags, t_date, t_amount):
        """Do input validation on arguments and initialize fields.

        Raise InvalidFieldValueError if argument is not expected or has
        invalid format.

        Args:
            t_type ():
            t_tags ():
            t_date ():
            t_amount ():
        """
        if t_type in SUPPORTED_TYPES:
            self._type = t_type
        else:
            raise InvalidFieldValueError(
                f'Invalid value {t_type} for transaction type'
            )

        try:
            tags_list = t_tags.split(",")
            self._tags = tags_list  # TODO: convert list to set
        except AttributeError:
            raise InvalidFieldValueError(
                f'Invalid value {t_tags} for transaction tags'
            )

        try:
            datetime.datetime.strptime(t_date, '%Y-%m-%d')
            self._date = t_date
        except ValueError:
            raise InvalidFieldValueError(
                f'Invalid value {t_date} for transaction date'
            )

        try:
            self._amount = float(t_amount)
        except ValueError:
            raise InvalidFieldValueError(
                f"Invalid value {t_amount} for transaction amount"
            )
        self._id = uuid.uuid4().hex

    def serialize(self):
        return {
            F_ID: self._id,
            F_TYPE: self._type,
            F_DATE: self._date,
            F_AMOUNT: self._amount,
            F_TAGS: self._tags
        }


class TransactionManager:
    @classmethod
    def create_transaction(cls, data):
        """Create a transaction from a dictionary instance.

        Args:
            data (dict): A dictionary with values for new transaction.
        """
        LoggingHelper.get_logger(cls.__name__).debug(
            f'creating new transaction with {data}'
        )

        try:
            transaction = Transaction(
                data[F_TYPE],
                data[F_TAGS],
                data[F_DATE],
                data[F_AMOUNT]
            )
        except KeyError as e:
            raise MissingFieldError(e)

        # keep id if was provided in data
        if F_ID in data:
            transaction._id = data[F_ID]

        return transaction

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
    def get_transactions(cls, filters=None):
        """Get transactions from db using a set of filters.
        """
        LoggingHelper.get_logger(cls.__name__).debug(
            'getting transactions from db using filters = {filters}'
        )
        db = DbFactory.get_db('csv')()
        return db.get_records(filters)

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
            f'removing transaction {id_value}'
        )
        db = DbFactory.get_db('csv')()
        db.remove_record(F_ID, id_value)

    @classmethod
    def update_transaction(cls, data):
        """Update a transaction in db by using the provided id and data.
        """
        if isinstance(data, Transaction):
            LoggingHelper.get_logger(cls.__name__).debug(
                f'updating transaction {data._id} with {data}'
            )
            db = DbFactory.get_db('csv')()
            db.edit_record(F_ID, data._id, data.serialize())
        else:
            raise InvalidTransactionError('invalid transaction object')
