import time
import serial
from util import FlyCommand

def get_command(receive):
    category = receive[0]
    property = receive[1]
    
    command = FlyCommand.NONE
    if category == 1:
        if property == 1:
            command = FlyCommand.TAKE_OFF
    elif category == 2:
        if property == 1:
            command = FlyCommand.LAND
    elif category == 3:
        if property == 1:
            command = FlyCommand.MOVE_LEFT
    elif category == 4:
        if property == 1:
            command = FlyCommand.MOVE_RIGHT
    elif category == 5:
        if property == 1:
            command = FlyCommand.MOVE_FORWARD
    elif category == 6:
        if property == 1:
            command = FlyCommand.MOVE_BACKWARD
    elif category == 7:
        if property == 1:
            command = FlyCommand.YOW_LEFT
    elif category == 8:
        if property == 1:
            command = FlyCommand.YOW_RIGHT

    return command

def voice_task(command_queue):
    # uart4 
    ser = serial.Serial("/dev/ttyAMA3", 115200)
    
    while True:
        count = ser.inWaiting()

        if count != 0:
            receive = ser.read(count)
            command = get_command(receive)
            command_queue.put(command, block=True)


