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

    def set_unique_colormap(self, item_count):
        # set color map to avoid repetition
        colormap = matplotlib.pyplot.cm.nipy_spectral
        self.axes.set_prop_cycle(color=[
            colormap(i) for i in numpy.linspace(0, 1, item_count)
        ])

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

        self.set_unique_colormap(len(line_values.keys()))

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

        self.set_unique_colormap(len(bar_values.keys()))

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


class PieChart(BaseChart):
    def draw(self, title, y_label, labels, section_values):
        """
        Draw a pie chart in the screen.
        """
        # explode section with highest value
        max_val = 0
        max_pos = -1
        for i in range(len(section_values)):
            if section_values[i] > max_val:
                max_val = section_values[i]
                max_pos = i
        explode = [0.0 for _ in range(len(section_values))]
        explode[max_pos] = 0.1

        self.set_unique_colormap(len(section_values))

        wedges, _, _ = self.axes.pie(
            section_values,
            explode=explode,
            autopct='%1.1f%%',
            textprops=dict(color='w')
        )
        self.axes.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        self.axes.legend(
            wedges,
            labels,
            bbox_to_anchor=(0.9, 1)
        )

        matplotlib.pyplot.show()


SUPPORTED_CHARTS = {'bar': BarChart, 'multiline': MultiLineChart, 'pie': PieChart}


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
