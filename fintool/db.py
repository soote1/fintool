"""A module that provides clients to manage data.

This module provides different types of objects
that can operate on data using different storage
mechanisms.

Supported clients:
    - FileDb

"""


class UnsupportedDbTypeError(Exception):
    """User defined error to be raised when a client
    requests an unsupported db type.
    """
    pass


class DbFactory:
    """An utility class to create a
    db object based on parameters.
    """

    @classmethod
    def get_db(cls, type):
        """Return a db object matching type
        argument.

        Raise UnsupportedDbTypeError if type is not
        included in SUPPORTED_TYPES variable.

        Args:
            type (str): Type of db object
        """

        try:
            return SUPPORTED_TYPES[type]
        except KeyError as e:
            raise UnsupportedDbTypeError(f"Db type not supported: {e}")


class AbstractDb:
    """Abstract class to define db behavior.
    """

    def add(self, item):
        pass

    def remove(self, item):
        pass

    def get(self, item):
        pass

    def edit(self, old, new):
        pass



class FileDb(AbstractDb):
    """A db object that operates on files.
    """

    def __init__(self, cfg):
        self._cfg = cfg

    def add_record(self, record):
        pass

    def remove_record(self, record_id):
        pass

    def get_record(self, record_id):
        pass

    def get_records(self, tags):
        pass

    def edit_record(self, record_id, new_record):
        pass


SUPPORTED_TYPES = {'file': FileDb}