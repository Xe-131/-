import threading
import time

def vision_task():
    while 1:
        print(1)
        time.sleep(1) 
        pass

def voice_task():
    while 1:
        print(2)
        time.sleep(2) 
        pass

lock = threading.Lock()

if __name__ == "__main__":
    vision_thread = threading.Thread(target=vision_task)
    voice_thread = threading.Thread(target=voice_task)

    vision_thread.start()
    voice_thread.start()

    vision_thread.join()
    voice_thread.join()

