import sys
import time
from random import randint
from threading import Thread
from time import sleep
from typing import Union

from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QPushButton, QLabel

from pglive.kwargs import Axis
from pglive.sources.data_connector import DataConnector
from pglive.sources.live_axis import LiveAxis
from pglive.sources.live_plot import LiveLinePlot, LiveVBarPlot,LiveScatterPlot
from pglive.sources.live_plot_widget import LivePlotWidget



class Window(QWidget):
    running = False

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)
        self.low_of_day: Union[float, None] = 5
        self.high_of_day: Union[float, None] = 15

        # Create one curve pre dataset
        high_plot = LiveLinePlot(pen="blue")
        low_plot = LiveLinePlot(pen="orange")
        mid_plot = LiveVBarPlot(  brush="green", pen="red",bar_width=0.005)
        # mid_plot = plot = LiveScatterPlot(brush='green')


        # Data connectors for each plot with dequeue of 600 points
        self.high_connector = DataConnector(high_plot, max_points=600)
        self.low_connector = DataConnector(low_plot, max_points=600)
        self.mid_connector = DataConnector(mid_plot, max_points=600)

        # Setup bottom axis with TIME tick format
        # You can use Axis.DATETIME to show date as well
        bottom_axis = LiveAxis("bottom", **{Axis.TICK_FORMAT: Axis.TIME})

        # Create plot itself
        self.chart_view = LivePlotWidget(title="Line Plot - Time series @ 2Hz", axisItems={'bottom': bottom_axis})
        # Show grid
        self.chart_view.showGrid(x=True, y=True, alpha=0.3)
        # Set labels
        self.chart_view.setLabel('bottom', 'Datetime', units="s")
        self.chart_view.setLabel('left', 'Price')
        # Add all three curves
        self.chart_view.addItem(mid_plot)
        self.chart_view.addItem(low_plot)
        self.chart_view.addItem(high_plot)

        # using -1 to span through all rows available in the window
        layout.addWidget(self.chart_view, 2, 0, -1, 3)

    def update(self):
        """Generate data at 2Hz"""
        while self.running:
            timestamp = time.time()

            # mid_px = randint(int((self.low_of_day + 2) * 100), int((self.high_of_day - 2) * 100)) / 100
            mid_px = randint(0,127)
            self.mid_connector.cb_append_data_point(mid_px, timestamp)
            self.low_connector.cb_append_data_point(self.low_of_day, timestamp)
            self.high_connector.cb_append_data_point(self.high_of_day, timestamp)

            print(f"epoch: {timestamp}, mid: {mid_px:.2f}")
            sleep(0.01)

    def start_app(self):
        """Start Thread generator"""
        self.running = True
        Thread(target=self.update).start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    window.start_app()
    app.exec()
    window.running = False