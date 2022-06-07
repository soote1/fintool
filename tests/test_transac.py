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

        self.transaction_manager = TransactionManager()

    def test_create_transaction(self):
        expected = {
            'type': 'income',
            'date': '2022-01-01',
            'amount': 12.3,
            'tags': {'a', 'b', 'c'}
        }

        actual = self.transaction_manager.create_transaction({
            'type': 'income',
            'date': '2022-01-01',
            'amount': '12.3',
            'tags': 'a|b|c'
        })

        # compare everything but id since it is uuid
        self.assertTrue(isinstance(actual.id, str))
        self.assertEqual(actual.type, expected['type'])
        self.assertEqual(actual.date, expected['date'])
        self.assertEqual(actual.amount, expected['amount'])
        self.assertEqual(actual.tags, expected['tags'])

    def test_save_transaction(self):
        """Just make sure that the test doesn't raises any error since
        other tests already validate db contents.
        """

        actual = self.transaction_manager.create_transaction({
            'type': 'income',
            'date': '2022-01-01',
            'amount': '12.3',
            'tags': 'a|b|c'
        })

        self.transaction_manager.save_transaction(actual)

    def test_get_transactions(self):
        expected = [
            self.transaction_manager.create_transaction({
                'id': '',
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': 'a|b|c'
            }),
            self.transaction_manager.create_transaction({
                'id': '',
                'type': 'income',
                'date': '2023-01-01',
                'amount': '121.3',
                'tags': 'd|e|f'
            })
        ]
        self.transaction_manager.save_transaction(
            self.transaction_manager.create_transaction({
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': 'a|b|c'
            })
        )
        self.transaction_manager.save_transaction(
            self.transaction_manager.create_transaction({
                'type': 'income',
                'date': '2023-01-01',
                'amount': '121.3',
                'tags': 'd|e|f'
            })
        )
        actual = self.transaction_manager.get_transactions()

        # compare everything but id
        for i in range(len(expected)):
            self.assertEqual(
                actual[i].type,
                expected[i].type,
                "transaction type not equal"
            )

            self.assertEqual(
                actual[i].date,
                expected[i].date,
                "transaction date not equal"
            )

            self.assertEqual(
                actual[i].amount,
                expected[i].amount,
                "transaction amount not equal"
            )

            self.assertEqual(
                actual[i].tags,
                expected[i].tags,
                "transaction tags not equal"
            )

    def test_get_transactions_with_filters(self):
        expected = [
            self.transaction_manager.create_transaction({
                'id': '',
                'type': 'outcome',
                'date': '2023-01-01',
                'amount': '121.3',
                'tags': 'd|e|f'
            })
        ]
        self.transaction_manager.save_transaction(
            self.transaction_manager.create_transaction({
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': 'a|b|c'
            })
        )
        self.transaction_manager.save_transaction(
            self.transaction_manager.create_transaction({
                'type': 'outcome',
                'date': '2023-01-01',
                'amount': '121.3',
                'tags': 'd|e|f'
            })
        )
        actual = self.transaction_manager.get_transactions(filters={
            'type': 'outcome'
        })

        # compare everything but id
        for i in range(len(expected)):
            self.assertEqual(
                actual[i].type,
                expected[i].type,
                "transaction type not equal"
            )

            self.assertEqual(
                actual[i].date,
                expected[i].date,
                "transaction date not equal"
            )

            self.assertEqual(
                actual[i].amount,
                expected[i].amount,
                "transaction amount not equal"
            )

            self.assertEqual(
                actual[i].tags,
                expected[i].tags,
                "transaction tags not equal"
            )

    def test_get_transactions_by_tags(self):
        expected = [
            self.transaction_manager.create_transaction({
                'id': '',
                'type': 'outcome',
                'date': '2023-01-01',
                'amount': '121.3',
                'tags': 'd|e|f'
            })
        ]
        self.transaction_manager.save_transaction(
            self.transaction_manager.create_transaction({
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': 'a|b|c'
            })
        )
        self.transaction_manager.save_transaction(
            self.transaction_manager.create_transaction({
                'type': 'outcome',
                'date': '2023-01-01',
                'amount': '121.3',
                'tags': 'd|e|f'
            })
        )
        actual = self.transaction_manager.get_transactions(filters={
            'tags': {'f'}
        })

        # compare everything but id
        for i in range(len(expected)):
            self.assertEqual(
                actual[i].type,
                expected[i].type,
                "transaction type not equal"
            )

            self.assertEqual(
                actual[i].date,
                expected[i].date,
                "transaction date not equal"
            )

            self.assertEqual(
                actual[i].amount,
                expected[i].amount,
                "transaction amount not equal"
            )

            self.assertEqual(
                actual[i].tags,
                expected[i].tags,
                "transaction tags not equal"
            )

    def test_remove_transaction(self):
        expected = []

        self.transaction_manager.save_transaction(
            self.transaction_manager.create_transaction({
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': 'a|b|c'
            })
        )
        actual = self.transaction_manager.get_transactions()
        self.transaction_manager.remove_transaction({'id': actual[0].id})
        actual = self.transaction_manager.get_transactions()

        self.assertEqual(actual, expected, "transaction list not equal")

    def test_edit_transaction(self):
        expected = [
            self.transaction_manager.create_transaction({
                'id': '9a80f28cbf5a4da0bcb1a4d6eed1796d',
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': 'a|b|c'
            })
        ]

        self.transaction_manager.save_transaction(
            self.transaction_manager.create_transaction({
                'id': '9a80f28cbf5a4da0bcb1a4d6eed1796d',
                'type': 'outcome',
                'date': '2022-02-02',
                'amount': '12.3',
                'tags': '1|2|3'
            })
        )

        self.transaction_manager.update_transaction(
            self.transaction_manager.create_transaction({
                'id': '9a80f28cbf5a4da0bcb1a4d6eed1796d',
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': 'a|b|c'
            })
        )

        actual = self.transaction_manager.get_transactions()

        self.assertEqual(
            actual[0].type,
            expected[0].type,
            "transaction type not equal"
        )

        self.assertEqual(
            actual[0].date,
            expected[0].date,
            "transaction date not equal"
        )

        self.assertEqual(
            actual[0].amount,
            expected[0].amount,
            "transaction amount not equal"
        )

        self.assertEqual(
            actual[0].tags,
            expected[0].tags,
            "transaction tags not equal"
        )
