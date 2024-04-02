import serial

ARDUINO_SERIAL_PORT = '/dev/ttyACM0'
ARDUINO_BAUD_RATE = 57600
TIMEOUT = 3

def convert_to_vars(bytes_in: bytes) -> tuple[int, int]:
    # return time in ms since board started as an int, and voltage on the pin in volts as a float

    a = int.from_bytes(bytes_in[0:2], byteorder='little')
    b = int.from_bytes(bytes_in[2:4], byteorder='little')

    return a, b

with serial.Serial(port=ARDUINO_SERIAL_PORT, baudrate=ARDUINO_BAUD_RATE, timeout=TIMEOUT) as arduino:    # implicitly calls arduino.close() afterwards
    while True:
        x = arduino.read(4)
        a, b = convert_to_vars(x)
        print(f"({a}, {b})")
