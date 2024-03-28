import serial
#import time
import re # regex, for text processing
import numpy as np  # for fixed-size arrays

ARDUINO_SERIAL_PORT = '/dev/ttyACM0'
ARDUINO_BAUD_RATE = 57600
TIMEOUT = 3
NUM_PD_READINGS_PER_CYCLE = 1000

# For reading from light sensor
ARDUINO_ADC_MAX_VOLTAGE = 5
ARDUINO_ADC_MAX_INT = 2**10     # changes depenging on board, but defaults to 10 bits on every board

def read_values(adno: serial.Serial):
    text_output = adno.readline().decode("ASCII")   # wait for arduinos to send a line of text over serial, then read it in

    m = re.search('^Time: (?P<current_time>[\d,\.]+), Humidity: (?P<humidity>[\d,\.]+)%, Temp:(?P<temperature>[\d,\.]+)C, Pressure: (?P<pressure>[\d,\.]+)Pa, Altitude: (?P<altitude>[\d,\.]+)m,  Temp (BMP) = (?P<temp2>[\d,\.]+)C, Light: (?P<light>[\d,\.]+)lx, \(Roll: (?P<roll>[\d,\.]+), Pitch: (?P<pitch>[\d,\.]+), Yaw: (?P<yaw>[\d,\.]+)\) deg$',text_output)
    if m:
        (current_time, humidity, temperature, pressure, altutude, temp2, light, roll, pitch, yaw) = [float(g) for g in m.groups()]
    else:
        current_time = humidity = temperature = pressure = altutude = temp2 = light = roll = pitch = yaw = None
        # In future: check for errors when noting is found

    return current_time, humidity, temperature, pressure, altutude, temp2, light, roll, pitch, yaw

def convert_serial_to_pd_reading(bytes_in: bytes) -> tuple[float, float]:
    # return time in ms since board started as an int, and voltage on the pin in volts as a float

    time_since_previous = (int.from_bytes(bytes_in[0:2], byteorder='little')*1e-4)     # Time is given in intervals of 1e-4 seconds
    voltage_on_pin = int.from_bytes(bytes_in[2:4], byteorder='little')*ARDUINO_ADC_MAX_VOLTAGE/ARDUINO_ADC_MAX_INT

    return time_since_previous, voltage_on_pin

with serial.Serial(port=ARDUINO_SERIAL_PORT, baudrate=ARDUINO_BAUD_RATE, timeout=TIMEOUT) as arduino:    # implicitly calls arduino.close() afterwards
    PD_time = 0
    while True:
        pd_times = np.empty(NUM_PD_READINGS_PER_CYCLE, 'f')
        pd_voltages = np.empty(NUM_PD_READINGS_PER_CYCLE, 'f')
        # TODO: flush serial and then wait for arduino to confirm that it's on the same page
        for c in range(NUM_PD_READINGS_PER_CYCLE):
            pd_time, pd_voltages[c] = convert_serial_to_pd_reading(arduino.read(4))
            pd_times[c] = PD_time = pd_time + PD_time

        sensor_time, humidity, temperature, pressure, altutude, temp2, light, roll, pitch, yaw = read_values(arduino)
        sensor_time = sensor_time*1e-3  # convert from miliseconds to seconds
        print(f"Time: {sensor_time}, Humidity: {humidity}%, Temp:{temperature}C, Pressure: {pressure}Pa,  Altitude: {altitude}m,  Temp (BMP) = {temp2}C, Light: {light}lx, (Roll: {roll}, Pitch: {pitch}, Yaw: {yaw}) deg")
        # Add to graph here
