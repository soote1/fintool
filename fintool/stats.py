"""
This module provides helper classes to perform statistic analysis
on data sets.
"""
import datetime
import calendar

from fintool.log import LoggingHelper


class OverallSummary:
    """A class to store and serialize a data set representing
    an overall summary.
    """
    def __init__(self, data, tags):
        self.__tags = tags
        self.__data = data
        self.__year = self.extract_year()
        self.__months = self.extract_months()
        self.__amounts_per_tag = self.extract_amount_per_tag()

    @property
    def year(self):
        return self.__year

    @property
    def months(self):
        return self.__months

    @property
    def amounts_per_tag(self):
        return self.__amounts_per_tag

    def get_data(self):
        return self.__data

    def extract_months(self):
        response = []
        for _, months in self.__data.items():
            for month, _ in months.items():
                response.append(calendar.month_name[month])
        return response

    def extract_amount_per_tag(self):
        amounts_per_tag = {}

        for _, months in self.__data.items():
            for _, monthly_data in months.items():
                for tag in self.__tags:
                    total = monthly_data['total_per_tag'].get(tag, 0)
                    try:
                        amounts_per_tag[tag].append(round(total, 2))
                    except:
                        amounts_per_tag[tag] = [round(total, 2)]
        return amounts_per_tag

    def extract_year(self):
        return list(self.__data.keys())[0]

    def get_chart_data(self):
        return {
            'title': f'Overall Summary',
            'ylabel': '$',
            'labels': self.months,
            'y_values': self.amounts_per_tag
        }

    def __str__(self):
        """Create a human readable representation of the
        data encapsulated by the class.
        """
        overall_summary = ''
        for year, months in self.__data.items():
            overall_summary = f'{overall_summary}Year: {year}\n'
            for month, monthly_data in months.items():
                month_name = f'Month: {calendar.month_name[month]}\n'
                overall_summary = f'{overall_summary}{month_name}'

                transactions_str = ''.join(
                    [str(tx) + '\n' for tx in monthly_data['transactions']]
                )
                overall_summary = f'{overall_summary}{transactions_str}\n'

                # I could use list comprehension but line is too long :(
                total_per_tag_strs = []
                for tag, total in monthly_data['total_per_tag'].items():
                    total_per_tag_strs.append(f'{tag}:\t{round(total, 2)}\n')
                total_per_tag_str = ''.join(total_per_tag_strs)
                overall_summary = f'{overall_summary}{total_per_tag_str}\n'

        return overall_summary


class StatsHelper:
    """An utility class to calculate stats on a dataset.
    """
    TRANSACTIONS = 'transactions'
    TOTAL_PER_TAG = 'total_per_tag'
    OVERALL_SUMMARY = 'overall_summary'

    def __init__(self, dataset):
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)
        self._logger.debug('initializing stats helper')
        self._dataset = dataset
        self._supported_stats = {
            self.OVERALL_SUMMARY: self.create_overall_summary
        }

    def create_stats(self, stats_type):
        """Identify the type of stats and calculate
        them by calling the appropriate method.
        """
        self._logger.debug('requested stats: %s', stats_type)
        try:
            return self._supported_stats[stats_type]()
        except KeyError:
            raise ValueError(f'unsupported stats type: {stats_type}')

    # TODO: think how to decouple transaction structure
    # maybe init, add, finish methods and pass values as args
    def create_overall_summary(self):
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
        self._logger.debug('creating overall summary')
        result = {}
        tags = set()
        for data in self._dataset:
            year = datetime.datetime.strptime(data.date, '%Y-%m-%d').year
            month = datetime.datetime.strptime(data.date, '%Y-%m-%d').month
            # add year if it doesn't exists
            if year not in result:
                result[year] = {}

            # add month if it doesn't exists for year
            if month not in result[year]:
                result[year][month] = {
                    self.TRANSACTIONS: [],
                    self.TOTAL_PER_TAG: {},
                }

            # append transaction in data[year][month][transactions]
            result[year][month][self.TRANSACTIONS].append(data)

            # insert tag and current value in data[year][month][total_per_tag]
            # or add current value to existing match
            for tag in data.tags:
                if tag in result[year][month][self.TOTAL_PER_TAG]:
                    result[year][month][self.TOTAL_PER_TAG][tag] += data.amount
                else:
                    result[year][month][self.TOTAL_PER_TAG][tag] = data.amount
                tags.add(tag)
        return OverallSummary(result, tags)
