import serial
# import time
import re  # regex, for text processing
import numpy as np  # for fixed-size arrays
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
# from PyQt6.QtWidgets import *
from PyQt6 import QtCore
import pyqtgraph as pg
import sys


ARDUINO_SERIAL_PORT = '/dev/ttyACM0'
ARDUINO_BAUD_RATE = 57600
TIMEOUT = 3
NUM_PD_READINGS_PER_CYCLE = 1000
NUM_BYTES_PER_READING = 4

# For reading from light sensor
ARDUINO_ADC_MAX_VOLTAGE = 5
ARDUINO_ADC_MAX_INT = 2 ** 10  # changes depending on board, but defaults to 10 bits on every board


def read_values(adno: serial.Serial):
    m = None
    counter = 0
    while m == None:
        text_output = adno.readline()
        try:
            text_output = text_output.decode(
                "ASCII")  # wait for arduinos to send a line of text over serial, then read it in
        except:
            split_string = b'Temp'
            text_output = split_string + test_str.split(split_string, 1)[1]
            try:
                text_output = text_output.decode("ASCII")
            except:
                counter += 1
                if counter >= 20:
                    raise Exception('Too many attempts')
        m = re.search(
            'Time: (?P<current_time>[\+,\-,\d,\.]+), Humidity: (?P<humidity>[\+,\-,\d,\.]+)%, Temp:(?P<temperature>[\+,\-,\d,\.]+)C, Pressure: (?P<pressure>[\+,\-,\d,\.]+)Pa, Altitude: (?P<altitude>[\+,\-,\d,\.]+)m, Temp \(BMP\): (?P<temp2>[\+,\-,\d,\.]+)C, Light: (?P<light>[\+,\-,\d,\.]+)lx, \(Roll: (?P<roll>[\+,\-,\d,\.]+), Pitch: (?P<pitch>[\+,\-,\d,\.]+), Yaw: (?P<yaw>[\+,\-,\d,\.]+)\) deg',
            text_output)
    if m:
        (current_time, humidity, temperature, pressure, altitude, temp2, light, roll, pitch, yaw) = [float(g) for g in
                                                                                                     m.groups()]
    else:
        current_time = humidity = temperature = pressure = altitude = temp2 = light = roll = pitch = yaw = None
        # In future: check for errors when noting is found

    return current_time, humidity, temperature, pressure, altitude, temp2, light, roll, pitch, yaw


def convert_serial_to_pd_reading(bytes_in: bytes) -> tuple[float, float]:
    # return time in ms since board started as an int, and voltage on the pin in volts as a float

    time_since_previous = (
                int.from_bytes(bytes_in[0:2], byteorder='little') * 1e-4)  # Time is given in intervals of 1e-4 seconds
    voltage_on_pin = int.from_bytes(bytes_in[2:4], byteorder='little') * ARDUINO_ADC_MAX_VOLTAGE / ARDUINO_ADC_MAX_INT

    return time_since_previous, voltage_on_pin


with serial.Serial(port=ARDUINO_SERIAL_PORT, baudrate=ARDUINO_BAUD_RATE,
                   timeout=TIMEOUT) as arduino:  # implicitly calls arduino.close() afterwards
    PD_time = 0
    while True:
        sensor_time, humidity, temperature, pressure, altitude, temp2, light, roll, pitch, yaw = read_values(arduino)
        sensor_time = sensor_time * 1e-3  # convert from miliseconds to seconds

        pd_times = np.empty(NUM_PD_READINGS_PER_CYCLE, 'f')
        pd_voltages = np.empty(NUM_PD_READINGS_PER_CYCLE, 'f')
        # TODO: flush serial and then wait for arduino to confirm that it's on the same page
        for c in range(NUM_PD_READINGS_PER_CYCLE):
            pd_time, pd_voltages[c] = convert_serial_to_pd_reading(arduino.read(NUM_BYTES_PER_READING))
            pd_times[c] = PD_time = pd_time + PD_time

        print(f"Average PD time: {np.average(pd_times)}; average PD value: {np.average(pd_voltages)}")
        print(
            f"Time: {sensor_time}, Humidity: {humidity}%, Temp:{temperature}C, Pressure: {pressure}Pa,  Altitude: {altitude}m,  Temp (BMP) = {temp2}C, Light: {light}lx, (Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}) deg")
        # Add to graph here

        class PlotWindowDynamicTemp(QMainWindow):
            def __init__(self):
                super().__init__()
                # Initialize plot widget, set it to the center, and set the background color to be white
                self.plot_graph = pg.PlotWidget()
                self.setCentralWidget(self.plot_graph)
                self.plot_graph.setBackground("w")

                # set the color and width of the plot line
                pen = pg.mkPen(color=(255, 0, 0), width=5)  # (r, g, b), i.e., (0, 0, 255) = blue, so first plot is set to red

                # set the title name, color, and size of the plot
                self.plot_graph.setTitle("Temperature vs Time", color='r', size='20pt')
                # styles = {"color": "red", "font-size": "18px"}

                # Axis Titles
                self.plot_graph.setLabel("left", "Temperature (ºC)", color="red")
                self.plot_graph.setLabel("bottom", "Time (sec)", color="red")

                # Legend and Gridlines
                self.plot_graph.addLegend()
                self.plot_graph.showGrid(x=True, y=True)

                # Arrays to store/update data readings from the two temperature sensors
                self.time = []
                self.temperature1 = []
                self.temperature2 = []

                # this instruction will plot data from the 1st temperature sensor
                self.line1 = self.plot_graph.plot(
                    self.time,
                    self.temperature2,
                    name="Temperature Sensor",  # Label for the legend
                    pen=pen,
                    symbol='o',
                    symbolSize=5,
                    symbolBrush='r'
                )
                pen = pg.mkPen(color=(0, 0, 255), width=5)  # (r, g, b) – set the second plot to blue

                # this will plot the second
                self.line2 = self.plot_graph.plot(
                    self.time,
                    self.temperature2,
                    name="Temperature Sensor (BMP)",  # Label for the legend
                    pen=pen,
                    symbol='o',
                    symbolSize=5,
                    symbolBrush='r'
                )

                # 1-second delay, we call the QTimer
                self.timer = QtCore.QTimer()
                self.timer.setInterval(1000)  # delay of 1000 milliseconds (1 second)
                self.timer.timeout.connect(self.update_plot)  # once the timer times out, call 'update_plot' fn
                self.timer.start()

            def update_plot(self):
                current_time_inner, humidity_inner, temperature_inner, pressure_inner, altitude1_inner, temp2_inner, light_inner, roll_inner, pitch_inner, yaw_inner = read_values()
                current_time_inner = current_time_inner * 1e-3

                self.time.append(current_time_inner)
                self.temperature1.append(temperature_inner)
                self.temperature2.append(temp2_inner)  # 2nd temperature value)
                # Update plot with new data
                self.line1.setData(self.time, self.temperature1)  # update plot for temperature 1
                self.line2.setData(self.time, self.temperature2)  # update plot for temperature 2

        class PlotWindowOptical(QMainWindow):
            def __init__(self):
                super().__init__()
                # initialize graph, center it, and set background colour
                self.plot_graph = pg.PlotWidget()
                self.setCentralWidget(self.plot_graph)
                self.plot_graph.setBackground("w")
                # set colour and thickness of plot line
                pen = pg.mkPen(color=(255, 255, 0), width=5)  # (r, g, b), i.e., (0, 255, 0) = green
                # set graph title, and axis titles
                self.plot_graph.setTitle("Voltage vs Time", color='k', size='20pt')
                self.plot_graph.setLabel('left', 'Voltage (V)', color='black')
                self.plot_graph.setLabel('bottom', 'Time (s)', color='black')

                # Legend and Gridlines
                self.plot_graph.addLegend()
                self.plot_graph.showGrid(x=True, y=True)

                self.time = []
                self.voltage = []

                self.line = self.plot_graph.plot(
                    self.time,
                    self.voltage,
                    name="Optical Path Reading",  # Label for the legend
                    pen=pen,
                    symbol='o',
                    symbolSize=5,
                    symbolBrush='b'
                )

                self.timer = QtCore.QTimer()
                self.timer.setInterval(1000)  # delay of 1000 milliseconds (1 second)
                self.timer.timeout.connect(self.update_plot_optical)  # once the timer times out, call 'update_plot' fn
                self.timer.start()

            def update_plot_optical(self):
                # Read values from Arduino
                time_since_previous_inner, voltage_on_pin_inner = convert_serial_to_pd_reading()
                # print(f"Time: {time_since_previous}, Voltage: {voltage_on_pin} V")

                # Update plot data for temperature
                # self.time.append(self.time[-1] + 1) if self.time else self.time.append(0)
                self.time.append(time_since_previous_inner)
                self.voltage.append(voltage_on_pin_inner)

                # Update plot with new data
                self.line.setData(self.time, self.voltage)

        class MainWindow(QMainWindow):  #this main window should show all the buttons that can be pressed for the different plots
            # *rn there is only buttons for the Temperature and Photodiode plots
            def __init__(self):
                super().__init__()
                self.window1 = PlotWindowDynamicTemp()
                self.window2 = PlotWindowOptical()

                self.setWindowTitle('Buttons')

                l = QVBoxLayout()
                button1 = QPushButton("Temperature vs. Time")
                button1.clicked.connect(self.toggle_window1)
                l.addWidget(button1)

                button2 = QPushButton("Voltage vs. Time")
                button2.clicked.connect(self.toggle_window2)
                l.addWidget(button2)

            def toggle_window1(self, checked):
                if self.window1.isVisible():
                    self.window1.hide()
                else:
                    self.window1.show()

            def toggle_window2(self, checked):
                if self.window2.isVisible():
                    self.window2.hide()
                else:
                    self.window2.show()

        app = QApplication(sys.argv)
        w = MainWindow()
        w.show()
        app.exec()
