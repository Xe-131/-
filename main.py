import threading
import queue
import cv2
import time
from vision import vision_task
from vision import vision_event
from voice import voice_task
from voice import voice_event
from fly import fly_task
from fly import fly_event
from util import FlyCommand 

if __name__ == "__main__":

    frame_queue = queue.Queue(maxsize=0)
    command_queue = queue.Queue(maxsize=0)

    vision_thread = threading.Thread(target=vision_task, args=(frame_queue, command_queue))
    voice_thread = threading.Thread(target=voice_task, args=(command_queue, ))
    fly_thread = threading.Thread(target=fly_task, args=(command_queue, ))

    # 跟随主线程关闭
    vision_thread.daemon = True
    voice_thread.daemon = True
    fly_thread.daemon = True

    vision_thread.start()
    vision_event.wait()

    voice_thread.start()
    voice_event.wait()

    fly_thread.start()
    fly_event.wait()

    # 主线程中显示图片
    while True:
        frame = frame_queue.get(block=True) 
        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            exit(1)

    vision_thread.join()
    voice_thread.join()
    fly_thread.join()

