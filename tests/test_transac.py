import pathlib
import unittest

from fintool.transac import TransactionManager


class TestTransactions(unittest.TestCase):
    """Test transactions module.
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

    def test_create_transaction(self):
        expected = {
            'type': 'income',
            'date': '2022-01-01',
            'amount': 12.3,
            'tags': ['a', 'b', 'c']
        }

        actual = TransactionManager.create_transaction({
            'type': 'income',
            'date': '2022-01-01',
            'amount': '12.3',
            'tags': 'a,b,c'
        })

        # compare everything but id since it is uuid
        self.assertTrue(isinstance(actual._id, str))
        self.assertEqual(actual._type, expected['type'])
        self.assertEqual(actual._date, expected['date'])
        self.assertEqual(actual._amount, expected['amount'])
        self.assertEqual(actual._tags, expected['tags'])

    def test_save_transaction(self):
        """Just make sure that the test doesn't raises any error since
        other tests already validate db contents.
        """

        actual = TransactionManager.create_transaction({
            'type': 'income',
            'date': '2022-01-01',
            'amount': '12.3',
            'tags': 'a,b,c'
        })

        TransactionManager.save_transaction(actual)

    def test_get_transactions(self):
        expected = [
            {
                'id': '',
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': "['a', 'b', 'c']"
            },
            {
                'id': '',
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': "['a', 'b', 'c']"
            }
        ]
        TransactionManager.save_transaction(
            TransactionManager.create_transaction({
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': 'a,b,c'
            })
        )
        TransactionManager.save_transaction(
            TransactionManager.create_transaction({
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': 'a,b,c'
            })
        )
        actual = TransactionManager.get_transactions()

        # compare everything but id
        for i in range(len(expected)):
            self.assertEqual(
                {k: actual[i][k] for k in actual[i].keys() - {'id'}},
                {k: expected[i][k] for k in expected[i].keys() - {'id'}},
                "transaction not equal"
            )

    def test_remove_transaction(self):
        expected = []

        TransactionManager.save_transaction(
            TransactionManager.create_transaction({
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': 'a,b,c'
            })
        )
        actual = TransactionManager.get_transactions()
        TransactionManager.remove_transaction({'id': actual[0]['id']})
        actual = TransactionManager.get_transactions()

        self.assertEqual(actual, expected, "transaction list not equal")

    def test_edit_transaction(self):
        expected = [
            {
                'id': '9a80f28cbf5a4da0bcb1a4d6eed1796d',
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': "['a', 'b', 'c']"
            }
        ]

        TransactionManager.save_transaction(
            TransactionManager.create_transaction({
                'id': '9a80f28cbf5a4da0bcb1a4d6eed1796d',
                'type': 'outcome',
                'date': '2022-02-02',
                'amount': '12.3',
                'tags': "1,2,3"
            })
        )

        TransactionManager.update_transaction(
            TransactionManager.create_transaction({
                'id': '9a80f28cbf5a4da0bcb1a4d6eed1796d',
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': "a,b,c"
            })
        )

        actual = TransactionManager.get_transactions()

        self.assertEqual(actual, expected, "transactions not equal")
