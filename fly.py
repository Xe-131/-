from util import FlyCommand 

import logging
import sys     
import time
from threading import Event

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig     
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.positioning.motion_commander import MotionCommander
from cflib.utils import uri_helper


URI = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E7E7')

DEFAULT_HEIGHT = 0.3
VELOCITY = 2
DISTANCE = 0.3
DEGREES = 30
RATE = DEGREES / 0.5


def fly(scf, commond_queue):
    # 起飞
    with MotionCommander(scf,default_height=DEFAULT_HEIGHT) as mc:
        while True:
            commond = commond_queue.get(block=True)

            if commond == FlyCommand.LAND:
                # 降落
                break 
            elif commond == FlyCommand.MOVE_RIGHT:
                mc.right(DISTANCE, velocity=VELOCITY) 
            elif commond == FlyCommand.MOVE_LEFT:
                mc.left(DISTANCE, velocity=VELOCITY) 
            elif commond == FlyCommand.MOVE_FORWARD:
                mc.forward(DISTANCE, velocity=VELOCITY) 
            elif commond == FlyCommand.MOVE_BACKWARD:
                mc.back(DISTANCE, velocity=VELOCITY) 
            elif commond == FlyCommand.YOW_LEFT:
                mc.turn_left(DEGREES, rate=RATE) 
            elif commond == FlyCommand.YOW_RIGHT:
                mc.turn_right(DEGREES, rate=RATE) 

        # mc.stop()
        
        

def fly_task(commond_queue):
    try:
        # deck_attached_event = Event()
        
        logging.basicConfig(level=logging.ERROR)

        cflib.crtp.init_drivers()

        # 开始通信
        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache="./cache")) as scf:
            scf.cf.platform.send_arming_request(True)
            time.sleep(1)
            
            # 判断flow 甲板是否连接
            
            # 在降落的状态下等待起飞命令
            while True:
                commond = commond_queue.get(block=True)

                if commond == FlyCommand.NONE:
                    pass
                elif commond == FlyCommand.TAKE_OFF:
                    fly(scf, commond_queue)    

    # 未连接无人机时自动测试
    except BaseException as e:
        while True:
            command = commond_queue.get(block=True) 
            print(command)
       

