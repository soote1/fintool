import unittest

import fintool.db

from tests.fixtures.util import remove_dir, TEST_DB_PATH


class TestCsvDb(unittest.TestCase):
    """Test CsvDb methods.
    """

    @classmethod
    def setUpClass(cls):
        cls.DB_DIR = TEST_DB_PATH
        cls.RECORDS_FILE = cls.DB_DIR.joinpath("records.csv")
        cls.FILE_DB = fintool.db.CsvDb(homedir=TEST_DB_PATH)
        cls.RECORDS_COLLECTION = 'records'

    def setUp(self):
        remove_dir(self.DB_DIR)

    def test_add_record(self):
        expected_header = 'a,b,c\n'
        expected_record = '1,2,"[\'a\', \'b\', \'c\']"\n'

        self.FILE_DB.add_record(
            {'a': 1, 'b': 2, 'c': ['a', 'b', 'c']},
            self.RECORDS_COLLECTION
        )

        with self.RECORDS_FILE.open() as f:
            lines = f.readlines()

        self.assertEqual(
            len(lines),
            2,
            "file doesn't contains expected record count"
        )

        self.assertEqual(
            lines[0],
            expected_header,
            "file doesn't contains expected headers"
        )

        self.assertEqual(
            lines[1],
            expected_record,
            "file doesn't contains expected record"
        )

    def test_remove_record(self):
        expected_content = 'a,b,c\n1,2,"[\'a\', \'b\', \'c\']"\n'

        self.FILE_DB.add_record(
            {'a': 1, 'b': 2, 'c': ['a', 'b', 'c']},
            self.RECORDS_COLLECTION
        )
        self.FILE_DB.add_record(
            {'a': 2, 'b': 3, 'c': ['a', 'b', 'c']},
            self.RECORDS_COLLECTION
        )
        self.FILE_DB.remove_record(
            id_field='a',
            id_value='2',
            collection=self.RECORDS_COLLECTION
        )

        with self.RECORDS_FILE.open() as f:
            actual_content = f.read()

        self.assertEqual(
            actual_content,
            expected_content,
            "file doesn't match expected content"
        )

    def test_get_records(self):
        expected_content = [
            {'a': '1', 'b': '2', 'c': "['a', 'b', 'c']"},
            {'a': '2', 'b': '3', 'c': "['a', 'b', 'c']"},
            {'a': '3', 'b': '4', 'c': "['a', 'b', 'c']"},
            {'a': '4', 'b': '5', 'c': "['a', 'b', 'c']"}
        ]

        self.FILE_DB.add_record(
            {'a': 1, 'b': 2, 'c': ['a', 'b', 'c']},
            self.RECORDS_COLLECTION
        )
        self.FILE_DB.add_record(
            {'a': 2, 'b': 3, 'c': ['a', 'b', 'c']},
            self.RECORDS_COLLECTION
        )
        self.FILE_DB.add_record(
            {'a': 3, 'b': 4, 'c': ['a', 'b', 'c']},
            self.RECORDS_COLLECTION
        )
        self.FILE_DB.add_record(
            {'a': 4, 'b': 5, 'c': ['a', 'b', 'c']},
            self.RECORDS_COLLECTION
        )

        actual_content = self.FILE_DB.get_records(self.RECORDS_COLLECTION)

        self.assertEqual(
            actual_content,
            expected_content,
            "file doesn't match expected content"
        )

    def test_edit_record(self):
        expected_content = 'a,b,c\n1,3,[\'a\']\n'

        self.FILE_DB.add_record(
            {'a': 1, 'b': 2, 'c': ['a', 'b', 'c']},
            self.RECORDS_COLLECTION
        )
        self.FILE_DB.edit_record(
            id_field='a',
            id_value='1',
            new_record={'a': 1, 'b': 3, 'c': ['a']},
            collection=self.RECORDS_COLLECTION
        )

        with self.RECORDS_FILE.open() as f:
            actual_content = f.read()

        self.assertEqual(
            actual_content,
            expected_content,
            "file doesn't match expected content"
        )
