from gpiozero import Button
from gpiozero import LED
from time import sleep
import serial
import time

#open serial
ser = serial.Serial("/dev/ttyAMA3", 115200)#set up serial
def main():
    while True:
        # 获得接收缓冲区字符
        count = ser.inWaiting()
        if count != 0:
            recv = ser.read(count)  #树莓派串口接收数据
            print(recv)         #树莓派串口发送数据
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        if ser != None:
            ser.close()
