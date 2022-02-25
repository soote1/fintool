"""
This module provides helper classes to perform statistic analysis
on data sets.
"""
import datetime


class StatsHelper:
    """An utility class to calculate stats on a dataset.
    """
    TRANSACTIONS = 'transactions'
    TOTAL_PER_TAG = 'total_per_tag'

    @classmethod
    def create_stats(cls, stats_type, data_set):
        """Identify the type of stats and calculate
        them by calling the appropriate method.
        """

    # TODO: think how to decouple transaction structure
    # maybe init, add, finish methods and pass values as args
    @classmethod
    def create_overall_summary(cls, dataset):
        """Calculate an overall summary from data_set.

        The returned object looks like the following structure:
        {
            2020: {
                1: {
                    transactions: [t1, t2, t3],
                    total_per_tag: {tag: total},
                }
            }
        }
        """
        result = {}
        for data in dataset:
            year = datetime.datetime.strptime(data.date, '%Y-%m-%d').year
            month = datetime.datetime.strptime(data.date, '%Y-%m-%d').month
            # add year if it doesn't exists
            if year not in result:
                result[year] = {}

            # add month if it doesn't exists for year
            if month not in result[year]:
                result[year][month] = {
                    cls.TRANSACTIONS: [],
                    cls.TOTAL_PER_TAG: {},
                }

            # append transaction in data[year][month][transactions]
            result[year][month][cls.TRANSACTIONS].append(data)

            # insert tag and current value in data[year][month][total_per_tag]
            # or add current value to existing match
            for tag in data.tags:
                if tag in result[year][month][cls.TOTAL_PER_TAG]:
                    result[year][month][cls.TOTAL_PER_TAG][tag] += data.amount
                else:
                    result[year][month][cls.TOTAL_PER_TAG][tag] = data.amount

            return result
