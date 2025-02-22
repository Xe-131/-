import threading
import queue
import cv2
import time
from vision  import vision_task

def voice_task(lock):
    while 1:
        with lock:
            print("voice task")

        time.sleep(2) 

# vision 与 voice 调用飞行函数
lock = threading.Lock()

if __name__ == "__main__":

    frame_queue = queue.Queue(maxsize=0)

    vision_thread = threading.Thread(target=vision_task, args=(lock, frame_queue))
    voice_thread = threading.Thread(target=voice_task, args=(lock, ))

    # 跟随主线程关闭
    vision_thread.daemon = True
    voice_thread.daemon = True

    vision_thread.start()
    voice_thread.start()

    # 主线程中显示图片
    while True:
        frame = frame_queue.get(block=True) 
        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            exit(1)

    vision_thread.join()
    voice_thread.join()

