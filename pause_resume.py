import signal
from threading import Thread

from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel

from pglive.sources.data_connector import DataConnector
from pglive.sources.live_plot import LiveScatterPlot,LiveVBarPlot
from pglive.sources.live_plot_widget import LivePlotWidget
from pglive.kwargs import LeadingLine

from pyqtgraph import mkPen

import random
import signal
import sys
from math import sin, cos
from time import sleep, time
from typing import List

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication

import mido
import rtmidi


running = True
app = QApplication(sys.argv)


def stop():
    """Stop current QApplication"""
    global running
    running = False
    app.exit(0)


def sin_wave_generator(*data_connectors, flip=False):
    """Sine wave generator"""
    x = 0
    while running:
        x += 1
        for data_connector in data_connectors:
            if flip:
                data_connector.cb_append_data_point(x, sin(x * 0.025))
            else:
                data_connector.cb_append_data_point(sin(x * 0.025), x)
        sleep(0.01)


def randint_generator(*data_connectors, flip=False):
    """Sine wave generator"""
    x = 0
    while running:
        # x += 1
        x = time()
        for data_connector in data_connectors:

            data_connector.cb_append_data_point(random.randint(0, 127), x)

        sleep(0.05)


def midi_res(*data_connectors, flip=False):
    
    outport=mido.open_output()
    
    inport=mido.open_input()
    
    while running:
    
        for note in inport.iter_pending():
            
            
            if note.type in ["note_on", "note_off"]:
                
                note_id = int(note.note) if note.note is not None else -1
            
            if note.type == "note_on":
                
                x = time()    
                
                print(f"note_on: {note_id}; velocity: {note.velocity}")
                
                data_connector.cb_append_data_point(note.velocity, x)
        
        sleep(0.01)

"""
Pause and Resume functionality of DataConnector is demonstrated in this example.
There are two buttons, that pause and resume live plotting.
When Live plot is paused, data are not collected.
"""
# Create parent widget
widget = LivePlotWidget(title="Line Plot @ 100Hz")
# plot = LiveVBarPlot()
# plot=LiveVBarPlot(  brush="green", pen="red",bar_width=0.01)
plot = LiveScatterPlot(brush="yellow", pen="red", size=10)
plot.set_leading_line(LeadingLine.HORIZONTAL, pen=mkPen("red"), text_axis=LeadingLine.AXIS_Y)
widget.addItem(plot)

# Create plot widget
parent_widget = QWidget()
parent_layout = QGridLayout()
parent_widget.setLayout(parent_layout)

# Connect plot with DataConnector
rate = 100
data_connector = DataConnector(plot, max_points=600, update_rate=rate, plot_rate=rate)

# Create Pause, Resume buttons and Live status label
pause_button = QPushButton("Pause live plot")
resume_button = QPushButton("Resume live plot")
status_label = QLabel("Live")

# Add widgets int parent widget
parent_layout.addWidget(widget)
parent_layout.addWidget(pause_button)
parent_layout.addWidget(resume_button)
parent_layout.addWidget(status_label)

# Connect signals with respective methods
pause_button.clicked.connect(data_connector.pause)
resume_button.clicked.connect(data_connector.resume)

# Connect sig_paused and sig_resume with live signal status label
data_connector.sig_paused.connect(lambda: status_label.setText("Paused"))
data_connector.sig_resumed.connect(lambda: status_label.setText("Live"))

parent_widget.show()

Thread(target=randint_generator, args=(data_connector,)).start()
# Thread(target=midi_res, args=(data_connector,)).start()
signal.signal(signal.SIGINT, lambda sig, frame: stop())
app.exec()
stop()
