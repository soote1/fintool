"""
This module provides clases to create and manage transactions.
"""


import uuid
import datetime

from fintool.db import DbFactory


class Error(Exception):
    """Base class for all errors in this module.
    """
    pass


class MissingFieldError(Error):
    pass


class InvalidFieldValueError(Error):
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
        try:
            return Transaction(
                data[F_TYPE],
                data[F_TAGS],
                data[F_DATE],
                data[F_AMOUNT]
            )
        except KeyError as e:
            raise MissingFieldError(e)

    @classmethod
    def save_transaction(cls, transaction):
        # TODO: need to get db type from cfg
        # TODO: need to inject db object so that we can test with mock data
        fintool_db = DbFactory.get_db('csv')()
        fintool_db.add_record(record=transaction.serialize())
