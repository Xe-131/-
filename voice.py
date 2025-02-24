import time
import serial
from util import FlyCommand
from threading import Event

voice_event = Event()

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
    print("\n初始化voice_task...")

    # uart4 
    try:
        ser = serial.Serial("/dev/ttyAMA3", 115200)
        if ser.isOpen():
            ser.reset_input_buffer()

            print("voice_task 初始化完毕\n")
            voice_event.set()
        else:
            print("voice_task 初始化失败: 打开uart4 失败")
    except BaseException as e:
        print("voice_task 初始化失败: /dev/ttyAMA3 未找到")
    
    voice_event.wait()
    while True:
        count = ser.inWaiting()
        if count != 2:
            ser.reset_input_buffer()
            # print(count)
            # time.sleep(1)
        else:
            print(f"count == {count}")
            receive = ser.read(count)
            command = get_command(receive)
            if command != FlyCommand.NONE:
                command_queue.put(command, block=True)
                print(receive)
            
        time.sleep(0.1)


