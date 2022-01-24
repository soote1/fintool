import unittest

import fintool.transac


class TestTransactions(unittest.TestCase):
    """Test transactions module.
    """

    def test_create_transaction(self):
        expected = {
            'type': 'income',
            'date': '2022-01-01',
            'amount': 12.3,
            'tags': ['a', 'b', 'c']
        }

        actual = fintool.transac.TransactionManager.create_transaction({
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

        actual = fintool.transac.TransactionManager.create_transaction({
            'type': 'income',
            'date': '2022-01-01',
            'amount': '12.3',
            'tags': 'a,b,c'
        })

        fintool.transac.TransactionManager.save_transaction(actual)
