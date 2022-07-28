import unittest

from fintool.transac import Transaction, TransactionManager
from tests.fixtures.util import remove_dir, TEST_DB_PATH


class TestTransactions(unittest.TestCase):
    """Test transactions module.
    """
    @classmethod
    def setUpClass(cls):
        cls.DB_DIR = TEST_DB_PATH
        cls.RECORDS_FILE = cls.DB_DIR.joinpath("records.csv")

    def setUp(self):
        remove_dir(self.DB_DIR)
        self.transaction_manager = TransactionManager()

    def test_create_transaction(self):
        expected = {
            'type': 'income',
            'date': '2022-01-01',
            'amount': 12.3,
            'tags': {'a', 'b', 'c'}
        }

        actual = Transaction(**{
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

        actual = Transaction(**{
            'type': 'income',
            'date': '2022-01-01',
            'amount': '12.3',
            'tags': 'a|b|c'
        })

        self.transaction_manager.save_transaction(actual)

    def test_get_transactions(self):
        from_str = '2022-01-01'
        to_str = '2023-01-01'
        expected = [
            Transaction(**{
                'id': '',
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': 'a|b|c'
            }),
            Transaction(**{
                'id': '',
                'type': 'income',
                'date': '2023-01-01',
                'amount': '121.3',
                'tags': 'd|e|f'
            })
        ]
        self.transaction_manager.save_transaction(
            Transaction(**{
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': 'a|b|c'
            })
        )
        self.transaction_manager.save_transaction(
            Transaction(**{
                'type': 'income',
                'date': '2023-01-01',
                'amount': '121.3',
                'tags': 'd|e|f'
            })
        )
        actual = self.transaction_manager.get_transactions(from_str, to_str)

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
        from_str = '2023-01-01'
        to_str = '2023-01-01'
        expected = [
            Transaction(**{
                'id': '',
                'type': 'outcome',
                'date': '2023-01-01',
                'amount': '121.3',
                'tags': 'd|e|f'
            })
        ]
        self.transaction_manager.save_transaction(
            Transaction(**{
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': 'a|b|c'
            })
        )
        self.transaction_manager.save_transaction(
            Transaction(**{
                'type': 'outcome',
                'date': '2023-01-01',
                'amount': '121.3',
                'tags': 'd|e|f'
            })
        )
        actual = self.transaction_manager.get_transactions(
            from_str,
            to_str,
            filters={'type': 'outcome'}
        )

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
        from_str = '2022-01-01'
        to_str = '2023-01-01'
        expected = [
            Transaction(**{
                'id': '',
                'type': 'outcome',
                'date': '2023-01-01',
                'amount': '121.3',
                'tags': 'd|e|f'
            })
        ]
        self.transaction_manager.save_transaction(
            Transaction(**{
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': 'a|b|c'
            })
        )
        self.transaction_manager.save_transaction(
            Transaction(**{
                'type': 'outcome',
                'date': '2023-01-01',
                'amount': '121.3',
                'tags': 'd|e|f'
            })
        )
        actual = self.transaction_manager.get_transactions(
            from_str,
            to_str,
            filters={'tags': {'f'}}
        )

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
        from_str = '2022-01-01'
        to_str = '2022-01-01'
        expected = []

        self.transaction_manager.save_transaction(
            Transaction(**{
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': 'a|b|c'
            })
        )
        actual = self.transaction_manager.get_transactions(from_str, to_str)
        self.transaction_manager.remove_transaction(
            from_str,
            actual[0].id
        )
        actual = self.transaction_manager.get_transactions(from_str, to_str)

        self.assertEqual(actual, expected, "transaction list not equal")

    def test_edit_transaction(self):
        from_str = '2022-01-01'
        to_str = '2022-02-02'
        expected = [
            Transaction(**{
                'id': '9a80f28cbf5a4da0bcb1a4d6eed1796d',
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': 'a|b|c'
            })
        ]

        self.transaction_manager.save_transaction(
            Transaction(**{
                'id': '9a80f28cbf5a4da0bcb1a4d6eed1796d',
                'type': 'outcome',
                'date': '2022-02-02',
                'amount': '12.3',
                'tags': '1|2|3'
            })
        )

        self.transaction_manager.update_transaction(
            to_str,
            Transaction(**{
                'id': '9a80f28cbf5a4da0bcb1a4d6eed1796d',
                'type': 'income',
                'date': '2022-01-01',
                'amount': '12.3',
                'tags': 'a|b|c'
            })
        )

        actual = self.transaction_manager.get_transactions(from_str, to_str)

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

    def test_calculate_namespace_from_date(self):
        """
        Make sure that TransactionManager knows how to create a collection
        namespace from a date string.
        """
        expected = '2020/01'
        input_data = '2020-01-01'
        actual = self.transaction_manager.calculate_collection_from_date(
            input_data
        )
        self.assertEqual(actual, expected, "namespace don't match")

    def test_calculate_namespaces_from_date_range(self):
        """
        Make sure that TransactionManager knows how to create a list of
        namespaces from a date range.
        """
        from_str = '2020-04-01'
        to_str = '2022-04-01'
        a = [
            '2020/04',
            '2020/05',
            '2020/06',
            '2020/07',
            '2020/08',
            '2020/09',
            '2020/10',
            '2020/11',
            '2020/12',
            '2021/01',
            '2021/02',
            '2021/03',
            '2021/04',
            '2021/05',
            '2021/06',
            '2021/07',
            '2021/08',
            '2021/09',
            '2021/10',
            '2021/11',
            '2021/12',
            '2022/01',
            '2022/02',
            '2022/03',
            '2022/04',
        ]
        b = self.transaction_manager.calculate_collections_from_date_range(
            from_str,
            to_str
        )

        self.assertEqual(a, b, 'list of namespaces not equal')

    def test_check_need_to_move_record_month(self):
        """
        Make sure that the TransactionManager can detect when to move a record.
        """
        old_date = '2020-01-02'
        new_date = '2020-02-02'

        actual = self.transaction_manager.check_need_to_move_record(
            old_date,
            new_date
        )

        self.assertTrue(actual, 'month is different, should be true')

    def test_check_need_to_move_record_year(self):
        """
        Make sure that the TransactionManager can detect when to move a record.
        """
        old_date = '2020-02-02'
        new_date = '2021-02-02'

        actual = self.transaction_manager.check_need_to_move_record(
            old_date,
            new_date
        )

        self.assertTrue(actual, 'year is different, should be true')

    def test_check_need_to_move_record_false(self):
        """
        Make sure that the TransactionManager can detect when to move a record.
        """
        old_date = '2020-02-02'
        new_date = '2020-02-03'

        actual = self.transaction_manager.check_need_to_move_record(
            old_date,
            new_date
        )

        self.assertFalse(actual, 'year and month are equal, should be false')
