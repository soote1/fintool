"""A module that provides clients to manage data.

This module provides different types of objects
that can operate on data using different storage
mechanisms.

Supported clients:
    - CsvDb

"""


import csv
import pathlib

from fintool.logging import LoggingHelper


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
            raise UnsupportedDbTypeError("Db type not supported: %s", e)


class AbstractDb:
    """Abstract class to define db behavior.
    """

    def add_record(self, record):
        pass

    def remove_record(self, id_field, id_value):
        pass

    def get_record(self, filter):
        pass

    def get_records(self):
        pass

    def edit_record(self, id_field, id_value, new_record):
        pass


class CsvDb(AbstractDb):
    """A db object that operates on csv files.
    """

    HOMEDIR = '~/.fintool'
    RECORDS_FILE = 'records.csv'
    RECORDS_FILE_TMP = 'records.csv.tmp'

    def __init__(self, homedir=HOMEDIR):
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        # create home dir
        self._homedir_path = pathlib.Path(homedir).expanduser()
        self._homedir_path.mkdir(parents=True, exist_ok=True)

        # create path to records file
        self._records_file = self._homedir_path.joinpath(self.RECORDS_FILE)
        self._records_file_tmp = self._homedir_path.joinpath(
            self.RECORDS_FILE_TMP
        )

    def add_record(self, record):
        """Add a new record into csv file.

        Args:
            record (dict): A dictionary representing the new record.
        """
        self._logger.debug('adding record to csv db %s', record)
        file_exists = self._records_file.is_file()
        with self._records_file.open('a', newline='') as csvfile:
            field_names = record.keys()
            writer = csv.DictWriter(csvfile, fieldnames=field_names)

            if not file_exists:
                writer.writeheader()
            writer.writerow(record)

    def remove_record(self, id_field, id_value):
        """Remove a record from csv file.

        Args:
            id_field (str): A string representing record's id field
            id_value (str): A string representing record's id value
        """
        self._logger.debug('removing record with id %s from csv db', id_value)
        with self._records_file.open('r', newline='') as records_csv_file:
            # create reader and get field names
            reader = csv.DictReader(records_csv_file)
            # field_names can't be None or DictWriter will complain
            field_names = reader.fieldnames if reader.fieldnames else []

            with self._records_file_tmp.open('w', newline='') as tmp_csv_file:
                # create writer to dump data in tmp file
                writer = csv.DictWriter(tmp_csv_file, fieldnames=field_names)
                writer.writeheader()

                # resume reading and write each row into tmp file
                for row in reader:
                    if row[id_field] != id_value:
                        writer.writerow(row)

        # replace original csv with tmp file
        pathlib.Path(self._records_file_tmp).replace(self._records_file)

    def get_records(self):
        """Return records from csv file that matches any filter in filters

        Args:
            filters (dict): a dictionary mapping keys with target values.
        """
        self._logger.debug('getting records from db')
        with self._records_file.open('r', newline='') as csvfile:
            result = []
            reader = csv.DictReader(csvfile)

            for row in reader:
                result.append(row)

            return result

    def edit_record(self, id_field, id_value, new_record):
        """Update a record with a new set of values while keeping id.

        Args:
            id_field (str): A string representing the name of id field
            id_value (str): A string representing the value of id field
            new_record (dict): A dictionary representing the new set of values
        """
        self._logger.debug('updating record %s with %s', id_value, new_record)
        with self._records_file.open('r', newline='') as records_csv_file:
            # create reader and get field names
            reader = csv.DictReader(records_csv_file)
            # field_names can't be None or DictWriter will complain
            field_names = reader.fieldnames if reader.fieldnames else []

            with self._records_file_tmp.open('w', newline='') as tmp_csv_file:
                # create writer to dump data in tmp file
                writer = csv.DictWriter(tmp_csv_file, fieldnames=field_names)
                writer.writeheader()

                # start reading rows from original csv file
                for row in reader:
                    # write row to tmp file if it is not the target row
                    if row[id_field] != id_value:
                        writer.writerow(row)
                    # otherwise write new record
                    else:
                        writer.writerow(new_record)

        # replace original csv with tmp file
        pathlib.Path(self._records_file_tmp).replace(self._records_file)


SUPPORTED_TYPES = {'csv': CsvDb}
