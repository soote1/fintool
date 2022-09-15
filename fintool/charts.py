import matplotlib.pyplot as plt
import numpy as np


class MultiLineChart:
    def draw(self, title, ylabel, labels, line_values):
        x = np.arange(len(labels))  # the label locations
        fig, ax = plt.subplots()

        # Build lines
        for label, y_values in line_values.items():
            ax.plot(x, y_values, label=label)

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xticks(x, labels)
        ax.legend()

        fig.tight_layout()

        plt.show()

class BarChart:
    def draw(self, title, ylabel, labels, bar_values):
        """"""
        x = np.arange(len(labels))  # the label locations
        fig, ax = plt.subplots()

        # Build bars
        bars_count = len(bar_values.keys())
        width = 1/bars_count  # the width of the bars
        bars = []
        for i, label_values in zip(range(bars_count), bar_values.items()):
            label, values = label_values
            bar_pos = x + width*i
            bar = ax.bar(bar_pos, values, width, label=label)
            bars.append(bar)

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xticks(x, labels)
        ax.legend()

        for bar in bars:
            ax.bar_label(bar, padding=3)

        fig.tight_layout()

        plt.show()
