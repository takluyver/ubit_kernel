from serial import Serial
from serial.tools.list_ports import comports

MICROBIT_PID = 516
MICROBIT_VID = 3368
BAUDRATE = 115200
PARITY = 'N'

def find_microbit():
    """
    Returns the port for the first micro:bit found connected to the computer.
    """
    for port in comports():
        if port.vid == MICROBIT_VID and port.pid == MICROBIT_PID:
            return port.device

def connect():
    """
    Returns a pySerial Serial object to talk to the microbit
    """
    return Serial(find_microbit(), BAUDRATE, parity=PARITY)
