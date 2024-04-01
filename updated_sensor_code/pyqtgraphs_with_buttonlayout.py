# ------------------------------------------------------
# technically outdated now but-
# *this is a version code for the UI integrating the previous main.py that Jonah uploaded*
# (display data for the DAQ and the Optical Path System)
# By: Matthew Yakubu
# Last Modified: March 28, 2024
# ------------------------------------------------------


from PyQt6.QtWidgets import *
from PyQt6 import QtCore
from random import randint
import sys
import pyqtgraph as pg
import serial
import re


# *this was put here so that I wouldn't need to repeat the instruction for each of the different windows
class ArduinoBase:
    def __init__(self):
        self.arduino = serial.Serial(port='/dev/ttyACM0', baudrate=57600, timeout=3)

# -------------------------------------------------------------------------------------------------------
# Function: PlotWindowDynamicLight
# Purpose: Plot the values from the Arduino Pressure sensor in lm(?)
# --------------------------------------------------------------------------------------------------------

class PlotWindowDynamicLight(QMainWindow, ArduinoBase):
    def __init__(self):
        super().__init__()

        # initialize the plot widget
        self.plot_graph = pg.PlotWidget()

        # aligned the plot widget and set its background color white
        self.setCentralWidget(self.plot_graph)
        self.plot_graph.setBackground("w")

        # set the color and width of the plot line
        pen = pg.mkPen(color=(0, 0, 255), width=5)  # (r, g, b), i.e., (0, 255, 0) = green

        # set the title name, color, and size of the plot
        self.plot_graph.setTitle("Light vs Time", color='k', size='20pt')

        # Axis Titles
        self.plot_graph.setLabel("left", "Luminous Flux (lm)", color="black")  # Y-axis Title
        self.plot_graph.setLabel("bottom", "Time (sec)", color="black")  # X-axis Title

        # Legend and Gridlines
        self.plot_graph.addLegend()
        self.plot_graph.showGrid(x=True, y=True)

        # self.time = list(range(10))
        # self.temperature = [randint(20, 40) for _ in range(10)]
        # * these were used when I was making random values my inputs for the plot(s) ^^

        self.time = []
        self.light = []

        # Get line reference
        self.line = self.plot_graph.plot(
            self.time,
            self.light,
            name="Pressure Sensor",  # Label for the legend
            pen=pen,
            symbol='o',
            symbolSize=5,
            symbolBrush='r'
        )

        # Initialize serial communication with Arduino
        # self.arduino = serial.Serial(port='/dev/ttyACM0', baudrate=57600, timeout=3)

        # for a 1-second delay, we call the QTimer
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)  # delay of 1000 milliseconds (1 second)
        self.timer.timeout.connect(self.update_plot)  # once the timer times out, call the 'update_plot' function
        self.timer.start()

    # ----------------------------------------------------------------------------------------
    # Function: update_plot – update the plot with data received from the Arduino sensor(s)
    # 1. Read values from the Arduino (Jonah)
    # 2. Update the plot (temperature specifically) for the measurement
    # 3. Update the plot for time
    # ----------------------------------------------------------------------------------------

    def update_plot(self):
        # Read values from Arduino
        current_time, humidity, temperature, pressure, light, roll, pitch, yaw = self.read_values()
        print(
            f"Time: {current_time}, Humidity: {humidity}%, Temp:{temperature}C, Pressure: {pressure}Pa, Light: {light}lx, (Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}) deg")

        # Update plot data for temperature
        self.time.append(self.time[-1] + 1) if self.time else self.time.append(0)
        self.light.append(light)

        # Update plot with new data
        self.line.setData(self.time, self.light)

        # Function to read values from Arduino

    # ----------------------------------------------------------------------------------------
    # Function: read_values –
    # ----------------------------------------------------------------------------------------

    def read_values(self):
        text_output = self.arduino.readline().decode('utf-8')

        m = re.search(
            '^Time: (?P<current_time>[\d,\.]+), Humidity: (?P<humidity>[\d,\.]+)%, Temp:(?P<temperature>[\d,\.]+)C, Pressure: (?P<pressure>[\d,\.]+)Pa, Light: (?P<light>[\d,\.]+)lx, \(Roll: (?P<roll>[\d,\.]+), Pitch: (?P<pitch>[\d,\.]+), Yaw: (?P<yaw>[\d,\.]+)\) deg$',
            text_output)
        if m:
            current_time, humidity, temperature, pressure, light, roll, pitch, yaw = [float(g) for g in m.groups()]
        else:
            current_time = humidity = temperature = pressure = light = roll = pitch = yaw = None

        return current_time, humidity, temperature, pressure, light, roll, pitch, yaw

# -------------------------------------------------------------------------------------------------------
# Function: PlotWindowDynamicPressure
# Purpose: Plot the values from the Arduino Pressure sensor in Pascals (Pa)
# --------------------------------------------------------------------------------------------------------


class PlotWindowDynamicPressure(QMainWindow, ArduinoBase):
    def __init__(self):
        super().__init__()

        # initialize the plot widget
        self.plot_graph = pg.PlotWidget()

        # aligned the plot widget and set its background color white
        self.setCentralWidget(self.plot_graph)
        self.plot_graph.setBackground("w")

        # set the color and width of the plot line
        pen = pg.mkPen(color=(0, 0, 255), width=5)  # (r, g, b), i.e., (0, 255, 0) = green

        # set the title name, color, and size of the plot
        self.plot_graph.setTitle("Pressure vs Time", color='b', size='20pt')
        # styles = {"color": "red", "font-size": "18px"}

        # Axis Titles
        self.plot_graph.setLabel("left", "Pressure (Pa)", color="blue")
        self.plot_graph.setLabel("bottom", "Time (sec)", color="blue")

        # Legend and Gridlines
        self.plot_graph.addLegend()
        self.plot_graph.showGrid(x=True, y=True)

        # Axis Ranges
        # (currently picking random values, need to switch in with sensor readings)
        # the range of the Y axis is currently set from 20 to 40

        # self.time = list(range(10))
        self.time = []
        self.pressure = []
        # self.temperature = [randint(20, 40) for _ in range(10)]

        # Get line reference
        self.line = self.plot_graph.plot(
            self.time,
            self.pressure,
            name="Pressure Sensor",  # Label for the legend
            pen=pen,
            symbol='o',
            symbolSize=5,
            symbolBrush='r'
        )

        # Initialize serial communication with Arduino
        # self.arduino = serial.Serial(port='/dev/ttyACM0', baudrate=57600, timeout=3)

        # 1-second delay, we call the QTimer
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)  # delay of 1000 milliseconds (1 second)
        self.timer.timeout.connect(self.update_plot)  # once the timer times out, call the 'update_plot' function
        self.timer.start()

    # plot update function
    def update_plot(self):
        # Read values from Arduino
        current_time, humidity, temperature, pressure, light, roll, pitch, yaw = self.read_values()
        print(
            f"Time: {current_time}, Humidity: {humidity}%, Temp:{temperature}C, Pressure: {pressure}Pa, Light: {light}lx, (Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}) deg")

        # Update plot data for temperature
        self.time.append(self.time[-1] + 1) if self.time else self.time.append(0)
        self.pressure.append(pressure)

        # Update plot with new data
        self.line.setData(self.time, self.pressure)

        # Function to read values from Arduino

    def read_values(self):
        text_output = self.arduino.readline().decode('utf-8')

        m = re.search(
            '^Time: (?P<current_time>[\d,\.]+), Humidity: (?P<humidity>[\d,\.]+)%, Temp:(?P<temperature>[\d,\.]+)C, Pressure: (?P<pressure>[\d,\.]+)Pa, Light: (?P<light>[\d,\.]+)lx, \(Roll: (?P<roll>[\d,\.]+), Pitch: (?P<pitch>[\d,\.]+), Yaw: (?P<yaw>[\d,\.]+)\) deg$',
            text_output)
        if m:
            current_time, humidity, temperature, pressure, light, roll, pitch, yaw = [float(g) for g in m.groups()]
        else:
            current_time = humidity = temperature = pressure = light = roll = pitch = yaw = None

        return current_time, humidity, temperature, pressure, light, roll, pitch, yaw

# -------------------------------------------------------------------------------------------------------
# Function: PlotWindowDynamicHumidity
# Purpose: Plot the values from the Humidity sensor in terms of percentage (%)
# -------------------------------------------------------------------------------------------------------


class PlotWindowDynamicHumidity(QMainWindow, ArduinoBase):
    def __init__(self):
        super().__init__()

        # initialize the plot widget
        self.plot_graph = pg.PlotWidget()

        # aligned the plot widget and set its background color white
        self.setCentralWidget(self.plot_graph)
        self.plot_graph.setBackground("w")

        # set the color and width of the plot line
        pen = pg.mkPen(color=(0, 255, 0), width=5)  # (r, g, b), i.e., (0, 255, 0) = green

        # set the title name, color, and size of the plot
        self.plot_graph.setTitle("Humidity vs Time", color='g', size='20pt')
        # styles = {"color": "red", "font-size": "18px"}

        # Axis Titles
        self.plot_graph.setLabel("left", "Humidity (%)", color="green")
        self.plot_graph.setLabel("bottom", "Time (sec)", color="green")

        # Legend and Gridlines
        self.plot_graph.addLegend()
        self.plot_graph.showGrid(x=True, y=True)

        # Axis Ranges
        # (currently picking random values, need to switch in with sensor readings)
        # the range of the Y axis is currently set from 20 to 40

        # self.time = list(range(10))
        self.time = []
        self.humidity = []
        # self.temperature = [randint(20, 40) for _ in range(10)]

        # Get line reference
        self.line = self.plot_graph.plot(
            self.time,
            self.humidity,
            name="Humidity Sensor",  # Label for the legend
            pen=pen,
            symbol='o',
            symbolSize=5,
            symbolBrush='r'
        )

        # Initialize serial communication with Arduino
        # self.arduino = serial.Serial(port='/dev/ttyACM0', baudrate=57600, timeout=3)

        # 1-second delay, we call the QTimer
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)  # delay of 1000 milliseconds (1 second)
        self.timer.timeout.connect(self.update_plot)  # once the timer times out, call the 'update_plot' function
        self.timer.start()

    # plot update function
    def update_plot(self):
        # Read values from Arduino
        current_time, humidity, temperature, pressure, light, roll, pitch, yaw = self.read_values()
        print(
            f"Time: {current_time}, Humidity: {humidity}%, Temp:{temperature}C, Pressure: {pressure}Pa, Light: {light}lx, (Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}) deg")

        # Update plot data for temperature
        self.time.append(self.time[-1] + 1) if self.time else self.time.append(0)
        self.humidity.append(humidity)

        # Update plot with new data
        self.line.setData(self.time, self.humidity)

        # Function to read values from Arduino

    def read_values(self):
        text_output = self.arduino.readline().decode('utf-8')

        m = re.search(
            '^Time: (?P<current_time>[\d,\.]+), Humidity: (?P<humidity>[\d,\.]+)%, Temp:(?P<temperature>[\d,\.]+)C, Pressure: (?P<pressure>[\d,\.]+)Pa, Light: (?P<light>[\d,\.]+)lx, \(Roll: (?P<roll>[\d,\.]+), Pitch: (?P<pitch>[\d,\.]+), Yaw: (?P<yaw>[\d,\.]+)\) deg$',
            text_output)
        if m:
            current_time, humidity, temperature, pressure, light, roll, pitch, yaw = [float(g) for g in m.groups()]
        else:
            current_time = humidity = temperature = pressure = light = roll = pitch = yaw = None

        return current_time, humidity, temperature, pressure, light, roll, pitch, yaw


class AnotherWindow(QWidget):  # we define another widget to create an additional window. * Any Widget without a parent
    # appears as a free-floating window.
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        # Set layout of window (vertically)
        layout = QVBoxLayout()

        # Set label and add it to the layout
        self.label = QLabel("Another Window %d" % randint(0, 100))
        layout.addWidget(self.label)
        self.setLayout(layout)

# -------------------------------------------------------------------------------------------------------
# Window: PlotWindowDynamicTemp
# Function: This window contains a dynamic plot with random values that self-updates every 1 second.
# *Switch to dynamic plot for temperature reading from Arduino sensor.
# --------------------------------------------------------------------------------------------------------


class PlotWindowDynamicTemp(QMainWindow, ArduinoBase):
    def __init__(self):
        super().__init__()

        # initialize the plot widget
        self.plot_graph = pg.PlotWidget()

        # aligned the plot widget and set its background color white
        self.setCentralWidget(self.plot_graph)
        self.plot_graph.setBackground("w")

        # set the color and width of the plot line
        pen = pg.mkPen(color=(0, 0, 255), width=5)  # (r, g, b), i.e., (0, 0, 255) = blue

        # set the title name, color, and size of the plot
        self.plot_graph.setTitle("Temperature vs Time", color='r', size='20pt')
        # styles = {"color": "red", "font-size": "18px"}

        # Axis Titles
        self.plot_graph.setLabel("left", "Temperature (ºC)", color="red")
        self.plot_graph.setLabel("bottom", "Time (sec)", color="red")

        # Legend and Gridlines
        self.plot_graph.addLegend()
        self.plot_graph.showGrid(x=True, y=True)

        # Axis Ranges
        # (currently picking random values, need to switch in with sensor readings)
        # the range of the Y axis is currently set from 20 to 40

        # self.time = list(range(10))
        self.time = []
        self.temperature = []
        # self.temperature = [randint(20, 40) for _ in range(10)]

        # Get line reference
        self.line = self.plot_graph.plot(
            self.time,
            self.temperature,
            name="Temperature Sensor",  # Label for the legend
            pen=pen,
            symbol='o',
            symbolSize=5,
            symbolBrush='r'
        )

        # Initialize serial communication with Arduino
        # self.arduino = serial.Serial(port='/dev/ttyACM0', baudrate=57600, timeout=3)

        # 1-second delay, we call the QTimer
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)  # delay of 1000 milliseconds (1 second)
        self.timer.timeout.connect(self.update_plot)  # once the timer times out, call the 'update_plot' function
        self.timer.start()

    # plot update function
    def update_plot(self):
        # Read values from Arduino
        current_time, humidity, temperature, pressure, light, roll, pitch, yaw = self.read_values()
        print(
            f"Time: {current_time}, Humidity: {humidity}%, Temp:{temperature}C, Pressure: {pressure}Pa, Light: {light}lx, (Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}) deg")

        # Update plot data for temperature
        self.time.append(self.time[-1] + 1) if self.time else self.time.append(0)
        self.temperature.append(temperature)

        # Update plot with new data
        self.line.setData(self.time, self.temperature)

        # Function to read values from Arduino
    def read_values(self):
        text_output = self.arduino.readline().decode('utf-8')

        m = re.search(
            '^Time: (?P<current_time>[\d,\.]+), Humidity: (?P<humidity>[\d,\.]+)%, Temp:(?P<temperature>[\d,\.]+)C, Pressure: (?P<pressure>[\d,\.]+)Pa, Light: (?P<light>[\d,\.]+)lx, \(Roll: (?P<roll>[\d,\.]+), Pitch: (?P<pitch>[\d,\.]+), Yaw: (?P<yaw>[\d,\.]+)\) deg$',
            text_output)
        if m:
            current_time, humidity, temperature, pressure, light, roll, pitch, yaw = [float(g) for g in m.groups()]
        else:
            current_time = humidity = temperature = pressure = light = roll = pitch = yaw = None

        return current_time, humidity, temperature, pressure, light, roll, pitch, yaw


class PlotWindowStaticTemp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.plot_graph = pg.PlotWidget()
        self.setCentralWidget(self.plot_graph)
        self.setWindowTitle('Temperature Plot')
        # align the plot widget and set its background color white
        self.plot_graph.setBackground("w")

        # set the color and width of the plot line
        pen = pg.mkPen(color=(255, 0, 0), width=5)  # (r, g, b)
        self.plot_graph.setTitle("Temperature vs Time", color='b', size='20pt')
        self.plot_graph.setLabel("left", "Temperature (ºC)", color="red")
        self.plot_graph.setLabel("bottom", "Time (sec)", color="red")
        # Legend and Gridlines
        self.plot_graph.addLegend()
        self.plot_graph.showGrid(x=True, y=True)

        minutes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 30]
        self.plot_graph.plot(minutes, temperature, name='Temperature sensor', pen=pen, symbol='o', symbolSize=5,
                             symbolBrush='b')


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.window1 = PlotWindowDynamicLight()
        self.window2 = PlotWindowDynamicPressure()
        self.window3 = PlotWindowDynamicHumidity()
        self.window4 = PlotWindowDynamicTemp()

        self.setWindowTitle('Buttons')
        l = QVBoxLayout()
        button1 = QPushButton("Light vs. Time \n (Dynamic Plot)")
        button1.clicked.connect(self.toggle_window1)
        l.addWidget(button1)

        button2 = QPushButton("Pressure vs. Time \n (Dynamic Plot)")
        button2.clicked.connect(self.toggle_window2)
        l.addWidget(button2)

        button3 = QPushButton("Humidity vs. Time \n (Dynamic Plot)")
        button3.clicked.connect(self.toggle_window3)
        l.addWidget(button3)

        button4 = QPushButton("Temperature vs. Time \n (Static Plot)")
        button4.clicked.connect(self.toggle_window4)
        l.addWidget(button4)

        w = QWidget()
        w.setLayout(l)
        self.setCentralWidget(w)

    # def show_new_window(self, checked):
        # if self.w is None:
        #    self.w = AnotherWindow()
        # self.w.show()

        # else:  # this means the window is already on the screen
        #    self.w.close()
        #    self.w = None  # discard the window
    def toggle_window1(self, checked):  # this will allow us to hide and present a new window without recreating it.
        if self.window1.isVisible():
            self.window1.hide()
        else:
            self.window1.show()

    def toggle_window2(self, checked):
        if self.window2.isVisible():
            self.window2.hide()
        else:
            self.window2.show()

    def toggle_window3(self, checked):
        if self.window3.isVisible():
            self.window3.hide()
        else:
            self.window3.show()

    def toggle_window4(self, checked):
        if self.window4.isVisible():
            self.window4.hide()
        else:
            self.window4.show()


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()
