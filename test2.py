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

def param_deck_flow(_, value_str):
    value = int(value_str) 
    print(f"{_}: {value}")
#     value = int(value_str)
#     print(value)
#     if value:
#         deck_attached_event.set()
#         print('Deck is attached!')
#     else:
#         print('Deck is NOT attached!')

def get_default_value_callback(_, value_str):
    value = value_str
    print(f"{_}: {value}")

if __name__ == '__main__':
    cflib.crtp.init_drivers()

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:

        start_time = time.perf_counter()


        print("decks using default_value:")
        scf.cf.param.get_default_value("deck.bcFlow2", get_default_value_callback)
        scf.cf.param.get_default_value("deck.bcZRanger2", get_default_value_callback)
        time.sleep(1)

        print("decks using update:")
        scf.cf.param.add_update_callback(group='deck', name='bcFlow2',
                                       cb=param_deck_flow)
        scf.cf.param.add_update_callback(group='deck', name='bcZRanger2',
                                       cb=param_deck_flow)
        time.sleep(1)

        print("decks using get_value:")
        print(scf.cf.param.get_value("deck.bcZRanger2", timeout=1))
        print(scf.cf.param.get_value("deck.bcFlow2", timeout=1))
        time.sleep(1)

        # Arm the Crazyflie
        scf.cf.platform.send_arming_request(True)
        time.sleep(1)

        end_time = time.perf_counter()
        print(end_time - start_time )
