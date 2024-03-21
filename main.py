import serial
#import time
import re # regex, for text processing

ARDUINO_SERIAL_PORT = '/dev/ttyACM0'
ARDUINO_BAUD_RATE = 57600
TIMEOUT = 3

def read_values(adno: serial.Serial):
    text_output = adno.readline()   # wait for arduinos to send a line of text over serial, then read it in

    m = re.search('^Time: (?P<current_time>[\d,\.]+), Humidity: (?P<humidity>[\d,\.]+)%, Temp:(?P<temperature>[\d,\.]+)C, Pressure: (?P<pressure>[\d,\.]+)Pa, Light: (?P<light>[\d,\.]+)lx, \(Roll: (?P<roll>[\d,\.]+), Pitch: (?P<pitch>[\d,\.]+), Yaw: (?P<yaw>[\d,\.]+)\) deg$',text_output)
    if m:
        (current_time, humidity, temperature, pressure, light, roll, pitch, yaw) = [float(g) for g in m.groups()]
    else:
        current_time = humidity = temperature = pressure = light = roll = pitch = yaw = None
        # In future: check for errors when noting is found

    return current_time, humidity, temperature, pressure, light, roll, pitch, yaw

with serial.Serial(port=ARDUINO_SERIAL_PORT, baudrate=ARDUINO_BAUD_RATE, timeout=TIMEOUT) as arduino:    # implicitly calls arduino.close() afterwards
    while True:
        current_time, humidity, temperature, pressure, light, roll, pitch, yaw = read_values(arduino)
        print(f"Time: {current_time}, Humidity: {humidity}%, Temp:{temperature}C, Pressure: {pressure}Pa, Light: {light}lx, (Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}) deg")
        # Add to graph here
