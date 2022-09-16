import abc
import numpy
import matplotlib.pyplot


class BaseChart(abc.ABC):
    """
    Abstract class to define base chart behavior.
    """
    def __init__(self):
        self.figure, self.axes = matplotlib.pyplot.subplots()

    @abc.abstractmethod
    def draw(self, title, ylabel, labels, y_values):
        """
        Must be implemented by concrete classes with logic
        to build the expected chart.
        """
        pass

    def show(self, y_label, title, x_values, x_labels):
        """
        Show the chart on the screen.
        """
        self.axes.set_ylabel(y_label)
        self.axes.set_title(title)
        self.axes.set_xticks(x_values, x_labels)
        self.axes.legend()
        self.figure.tight_layout()
        matplotlib.pyplot.show()


class MultiLineChart(BaseChart):
    def draw(self, title, y_label, labels, line_values):
        """
        Draw a multiline chart in the screen.
        """
        x_values = numpy.arange(len(labels))

        # Build lines
        for label, y_values in line_values.items():
            self.axes.plot(x_values, y_values, label=label)

        self.show(y_label, title, x_values, labels)


class BarChart(BaseChart):
    def draw(self, title, y_label, labels, bar_values):
        """
        Draw a bar chart in the screen.
        """
        x_values = numpy.arange(len(labels))

        # Build bars
        bars_count = len(bar_values.keys())
        width = 1/bars_count  # the width of the bars
        bars = []
        for i, label_values in zip(range(bars_count), bar_values.items()):
            label, values = label_values
            bar_pos = x_values + width*i
            bar = self.axes.bar(bar_pos, values, width, label=label)
            bars.append(bar)

        for bar in bars:
            self.axes.bar_label(bar, padding=3)

        self.show(y_label, title, x_values, labels)


SUPPORTED_CHARTS = {'bar': BarChart, 'multiline': MultiLineChart}


class UnsupportedChartTypeError(Exception):
    """
    Raised when user requested an invalid chart type.
    """
    pass


class ChartFactory:
    """
    Helper class to build a supported chart.
    """
    @staticmethod
    def build_chart(chart_type):
        try:
            return SUPPORTED_CHARTS[chart_type]()
        except KeyError as e:
            raise UnsupportedChartTypeError(f'Chart type not supported: {e}')
