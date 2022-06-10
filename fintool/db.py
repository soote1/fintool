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


class Error(Exception):
    """
    Base class for errors in this module.
    """


class UnsupportedDbTypeError(Error):
    """User defined error to be raised when a client
    requests an unsupported db type.
    """


class MissingCollectionError(Error):
    """
    Raised when the collection does not exist.
    """


class DbFactory:
    """An utility class to create a
    db object based on parameters.
    """

    @classmethod
    def get_db(cls, db_type):
        """Return a db object matching type
        argument.

        Raise UnsupportedDbTypeError if type is not
        included in SUPPORTED_TYPES variable.

        Args:
            type (str): Type of db object
        """

        try:
            return SUPPORTED_TYPES[db_type]
        except KeyError as key_error:
            raise UnsupportedDbTypeError(f"Db type not supported: {key_error}")


class AbstractDb:
    """Abstract class to define db behavior.
    """

    def add_record(self, record, collection):
        pass

    def remove_record(self, id_field, id_value, collection):
        pass

    def get_records(self, collection):
        pass

    def edit_record(self, id_field, id_value, new_record, collection):
        pass


class CsvDb(AbstractDb):
    """A db object that operates on csv files.
    """

    HOMEDIR = '~/.fintool'
    RECORDS_FILE = '{}.csv'
    RECORDS_FILE_TMP = '{}.csv.tmp'

    def __init__(self, homedir=HOMEDIR):
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        # create home dir
        self._homedir_path = pathlib.Path(homedir).expanduser()
        self._homedir_path.mkdir(parents=True, exist_ok=True)
        super().__init__()

    def create_collection_objects(self, collection):
        """
        Create file objects to manage records in collection file and return
        them in a tuple.
        """
        records_file = self._homedir_path.joinpath(
            self.RECORDS_FILE.format(collection)
        )
        # create dir if not exists
        records_file.parent.mkdir(parents=True, exist_ok=True)
        records_tmp_file = self._homedir_path.joinpath(
            self.RECORDS_FILE_TMP.format(collection)
        )
        return (records_file, records_tmp_file)

    def add_record(self, record, collection):
        """Add a new record into csv file.

        Args:
            record (dict): A dictionary representing the new record.
        """
        self._logger.debug('adding record to csv db %s', record)
        collection_file, _ = self.create_collection_objects(collection)
        file_exists = collection_file.is_file()
        with collection_file.open(
            'a',
            newline='',
            encoding='utf-8',
        ) as csvfile:
            field_names = record.keys()
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            # write header if file didn't exists before trying to open it.
            if not file_exists:
                writer.writeheader()
            writer.writerow(record)

    def remove_record(self, id_field, id_value, collection):
        """Remove a record from csv file.

        Args:
            id_field (str): A string representing record's id field
            id_value (str): A string representing record's id value
        """
        self._logger.debug('removing record with id %s from csv db', id_value)
        collection_file, collection_tmp_file = self.create_collection_objects(
            collection
        )
        try:
            with collection_file.open(
                'r',
                newline='',
                encoding='utf-8',
            ) as records_csv_file:
                # create reader and get field names
                reader = csv.DictReader(records_csv_file)
                # field_names can't be None or DictWriter will complain
                field_names = reader.fieldnames if reader.fieldnames else []

                with collection_tmp_file.open(
                    'w',
                    encoding='utf-8',
                    newline=''
                ) as tmp_csv_file:
                    # create writer to dump data in tmp file
                    writer = csv.DictWriter(
                        tmp_csv_file,
                        fieldnames=field_names
                    )
                    writer.writeheader()

                    # resume reading and write each row into tmp file
                    for row in reader:
                        if row[id_field] != id_value:
                            writer.writerow(row)
        except FileNotFoundError:
            raise MissingCollectionError(
                f'The collection {collection} does not exists'
            )

        # replace original csv with tmp file
        pathlib.Path(collection_tmp_file).replace(collection_file)

    def get_records(self, collection):
        """Return records from csv file that matches any filter in filters

        Args:
            filters (dict): a dictionary mapping keys with target values.
        """
        result = []
        self._logger.debug('getting records from db')
        collection_file, _ = self.create_collection_objects(collection)
        try:
            with collection_file.open(
                'r',
                newline='',
                encoding='utf-8',
            ) as csvfile:
                result = []
                reader = csv.DictReader(csvfile)

                for row in reader:
                    result.append(row)
        except FileNotFoundError:
            raise MissingCollectionError(
                f'The collection {collection} does not exist'
            )
        return result

    def edit_record(self, id_field, id_value, new_record, collection):
        """Update a record with a new set of values while keeping id.

        Args:
            id_field (str): A string representing the name of id field
            id_value (str): A string representing the value of id field
            new_record (dict): A dictionary representing the new set of values
        """
        self._logger.debug('updating record %s with %s', id_value, new_record)
        collection_file, collection_tmp_file = self.create_collection_objects(
            collection
        )
        try:
            with collection_file.open(
                'r',
                newline='',
                encoding='utf-8',
            ) as records_csv_file:
                # create reader and get field names
                reader = csv.DictReader(records_csv_file)
                # field_names can't be None or DictWriter will complain
                field_names = reader.fieldnames if reader.fieldnames else []

                with collection_tmp_file.open(
                    'w',
                    encoding='utf-8',
                    newline=''
                ) as tmp_csv_file:
                    # create writer to dump data in tmp file
                    writer = csv.DictWriter(
                        tmp_csv_file,
                        fieldnames=field_names
                    )
                    writer.writeheader()

                    # start reading rows from original csv file
                    for row in reader:
                        # write row to tmp file if it is not the target row
                        if row[id_field] != id_value:
                            writer.writerow(row)
                        # otherwise write new record
                        else:
                            writer.writerow(new_record)
        except FileNotFoundError:
            raise MissingCollectionError(
                f'The collection {collection} does not exists'
            )

        # replace original csv with tmp file
        pathlib.Path(collection_tmp_file).replace(collection_file)


SUPPORTED_TYPES = {'csv': CsvDb}
