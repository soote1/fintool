import unittest

from fintool.transac import Transaction
from fintool.stats import StatsHelper, OverallSummary


class TestStats(unittest.TestCase):
    """"""
    @classmethod
    def setUpClass(cls):
        cls.transactions = [
            Transaction(**{
                'type': 'outcome',
                'date': '2022-01-01',
                'amount': '200.5',
                'tags': 'food|uber'
            }),
            Transaction(**{
                'type': 'outcome',
                'date': '2022-01-02',
                'amount': '300.5',
                'tags': 'food|uber'
            }),
            Transaction(**{
                'type': 'outcome',
                'date': '2022-02-01',
                'amount': '400.5',
                'tags': 'food|uber'
            }),
            Transaction(**{
                'type': 'outcome',
                'date': '2022-02-02',
                'amount': '200.5',
                'tags': 'food|fresko'
            }),
            Transaction(**{
                'type': 'outcome',
                'date': '2022-03-01',
                'amount': '500',
                'tags': 'transportation|uber'
            }),
            Transaction(**{
                'type': 'outcome',
                'date': '2022-03-02',
                'amount': '200.5',
                'tags': 'transportation|uber'
            }),
            Transaction(**{
                'type': 'outcome',
                'date': '2023-01-01',
                'amount': '12',
                'tags': 'food|fresko'
            }),
            Transaction(**{
                'type': 'outcome',
                'date': '2023-01-02',
                'amount': '400',
                'tags': 'food|fresko'
            }),
            Transaction(**{
                'type': 'outcome',
                'date': '2023-02-01',
                'amount': '500',
                'tags': 'food|fresko'
            }),
            Transaction(**{
                'type': 'outcome',
                'date': '2023-02-02',
                'amount': '100.5',
                'tags': 'transportation|uber'
            }),
        ]

        # remove guid from transactions so that we can match them
        for tx in cls.transactions:
            tx.id = ''

    def test_create_overall_summary(self):
        expected = {
            2022: {
                1: {
                    'transactions': [
                        self.transactions[0],
                        self.transactions[1]
                    ],
                    'total_per_tag': {'food': 501, 'uber': 501}
                },
                2: {
                    'transactions': [
                        self.transactions[2],
                        self.transactions[3]
                    ],
                    'total_per_tag': {
                        'food': 601,
                        'uber': 400.5,
                        'fresko': 200.5
                    }
                },
                3: {
                    'transactions': [
                        self.transactions[4],
                        self.transactions[5]
                    ],
                    'total_per_tag': {'transportation': 700.5, 'uber': 700.5}
                }
            },
            2023: {
                1: {
                    'transactions': [
                        self.transactions[6],
                        self.transactions[7]
                    ],
                    'total_per_tag': {'food': 412, 'fresko': 412}
                },
                2: {
                    'transactions': [
                        self.transactions[8],
                        self.transactions[9]
                    ],
                    'total_per_tag': {
                        'transportation': 100.5,
                        'food': 500,
                        'fresko': 500,
                        'uber': 100.5
                    }
                }
            }
        }

        stats_helper = StatsHelper(self.transactions)
        actual = stats_helper.create_overall_summary()

        self.assertEqual(expected, actual.get_data())
