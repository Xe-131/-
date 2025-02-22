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

deck_attached_event = Event()

logging.basicConfig(level=logging.ERROR)

DEFAULT_HEIGHT = 0.3

def take_off_simple(scf):
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:

        start_time = time.perf_counter()

        time.sleep(1)
        mc.right(0.3, velocity = 2)
        time.sleep(1)
        mc.left(0.5, velocity = 2)
        time.sleep(1)
        mc.forward(0.3, velocity = 2)
        time.sleep(1)
        mc.back(0.3, velocity = 2)
        time.sleep(1)

        end_time = time.perf_counter()
        print(end_time - start_time)

        mc.stop()

if __name__ == '__main__':
    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
#         # Arm the Crazyflie
#         scf.cf.platform.send_arming_request(True)
#         time.sleep(3.0)
# 
#         # 检查flowv2 连接
#         is_flowv2_attached = scf.cf.param.get_value("deck.bcFlow2", timeout=1)
#         time.sleep(1.0)
#         take_off = 0
#         if is_flowv2_attached:
#             print("deck.bcFlow2 is attached")
#             take_off = 1
#         else:
#             print("deck.bcFlow2 is NOT  attached")
#             sys.exit()
# 
#         # 起飞 
#         if take_off == 0:
#             sys.exit()

        take_off_simple(scf)
        time.sleep(1)

