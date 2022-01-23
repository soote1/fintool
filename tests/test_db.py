import pathlib
import unittest

import fintool.db


class TestCsvDb(unittest.TestCase):
    """Test CsvDb methods.
    """

    @classmethod
    def setUpClass(cls):
        cls.DB_DIR = pathlib.Path('~/.fintool').expanduser()
        cls.RECORDS_FILE = cls.DB_DIR.joinpath("records.csv")

    def setUp(self):
        try:
            for f in self.DB_DIR.glob("*"):
                f.unlink()

            self.DB_DIR.rmdir()
        except FileNotFoundError:
            pass  # db doesn't exists

    def test_create_db(self):

        file_db = fintool.db.DbFactory.get_db('csv')()

        self.assertTrue(
            isinstance(file_db, fintool.db.CsvDb),
            "file_db not an instance of CsvDb"
        )
        self.assertTrue(self.DB_DIR.exists(), "fintool db doesn't exists")

    def test_add_record(self):
        expected_header = 'a,b,c\n'
        expected_record = '1,2,"[\'a\', \'b\', \'c\']"\n'

        file_db = fintool.db.CsvDb()
        file_db.add_record({'a': 1, 'b': 2, 'c': ['a', 'b', 'c']})

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

        file_db = fintool.db.CsvDb()
        file_db.add_record({'a': 1, 'b': 2, 'c': ['a', 'b', 'c']})
        file_db.add_record({'a': 2, 'b': 3, 'c': ['a', 'b', 'c']})
        file_db.remove_record(id_field='a', id_value='2')

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

        file_db = fintool.db.CsvDb()

        file_db.add_record({'a': 1, 'b': 2, 'c': ['a', 'b', 'c']})
        file_db.add_record({'a': 2, 'b': 3, 'c': ['a', 'b', 'c']})
        file_db.add_record({'a': 3, 'b': 4, 'c': ['a', 'b', 'c']})
        file_db.add_record({'a': 4, 'b': 5, 'c': ['a', 'b', 'c']})

        actual_content = file_db.get_records()

        self.assertEqual(
            actual_content,
            expected_content,
            "file doesn't match expected content"
        )

    def test_get_records_with_filters(self):
        expected_content = [
            {'a': '4', 'b': '5', 'c': "['a']"},
        ]

        file_db = fintool.db.CsvDb()

        file_db.add_record({'a': 1, 'b': 2, 'c': ['a', 'b', 'c']})
        file_db.add_record({'a': 2, 'b': 3, 'c': ['a', 'b', 'c']})
        file_db.add_record({'a': 3, 'b': 4, 'c': ['a', 'b', 'c']})
        file_db.add_record({'a': 4, 'b': 5, 'c': ['a', 'b', 'c']})
        file_db.add_record({'a': 4, 'b': 5, 'c': ['a']})

        actual_content = file_db.get_records(filters={'c': ["['a']"]})

        self.assertEqual(
            actual_content,
            expected_content,
            "file doesn't match expected content"
        )

    def test_edit_record(self):
        expected_content = 'a,b,c\n1,3,[\'a\']\n'

        file_db = fintool.db.CsvDb()
        file_db.add_record({'a': 1, 'b': 2, 'c': ['a', 'b', 'c']})
        file_db.edit_record(
            id_field='a',
            id_value='1',
            new_record={'a': 1, 'b': 3, 'c': ['a']}
        )

        with self.RECORDS_FILE.open() as f:
            actual_content = f.read()

        self.assertEqual(
            actual_content,
            expected_content,
            "file doesn't match expected content"
        )
