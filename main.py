import cv2
from picamera2 import Picamera2
from libcamera import Transform
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from util import draw_landmarks_on_image
from util import is_finger_bend
from util import get_gesture_onehand
from util import get_command
from util import img_width  
from util import img_height 
from util import FlyCommand


if __name__ == "__main__":
    # 初始化相机
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (img_width, img_height)}, transform=Transform(vflip=True)))
    picam2.start()
    
    # 初始化FPS 计算 
    prev_time = time.time()  
    frame_count = 0  
    fps = 0
     
    # 配置模型
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(base_options=base_options, 
                                           # running_mode="IMAGE",
                                           num_hands=2,
                                           min_tracking_confidence=0.5,
                                           min_hand_detection_confidence=0.1,
                                           min_hand_presence_confidence=0.5)
    
    detector = vision.HandLandmarker.create_from_options(options) 
    
    # 最近frame_num 次命令(未识别到手掌为NONE)
    frame_num = 5
    command_history = list(range(frame_num))
    
    while True:
        # 捕获一帧图像(BGR)
        img_BGR = picam2.capture_array()
        
        # 计算FPS 并显示
        frame_count += 1
        curr_time = time.time()
        elapsed_time = curr_time - prev_time
        # 每秒更新一次FPS
        if elapsed_time >= 1:  
            fps = frame_count / elapsed_time
            prev_time = curr_time
            frame_count = 0
        cv2.putText(img_BGR, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    
        # 图片转换
        img_RGB = cv2.cvtColor(img_BGR, cv2.COLOR_BGR2RGB)
        img_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_RGB)
    
        # 模型推断
        detection_result = detector.detect(img_mp)
    
        # 模型是否识别到手掌
        if len(detection_result.hand_landmarks) == 0:
            cv2.imshow("Camera", img_BGR)
            command = FlyCommand.NONE
        else:
    
            # 单手
            if len(detection_result.hand_landmarks) == 1: 
                command = FlyCommand.NONE
            # 双手
            else:
                # 判断双手手势
                finger_state_0 = is_finger_bend(detection_result.hand_landmarks[0])
                finger_state_1 = is_finger_bend(detection_result.hand_landmarks[1])
                gesture_0 = get_gesture_onehand(detection_result.hand_landmarks[0], finger_state_0, detection_result.handedness[0][0].category_name)
                gesture_1 = get_gesture_onehand(detection_result.hand_landmarks[1], finger_state_1, detection_result.handedness[1][0].category_name)
                # 判断命令(保证get_command 参数先左后右)
                if detection_result.handedness[0][0].category_name == "Right":
                    command = get_command(gesture_0, gesture_1)
                else:
                    command = get_command(gesture_1, gesture_0)
                    
            # 标注图像
            annotated_image = draw_landmarks_on_image(img_mp.numpy_view(), detection_result) 
    
            # 显示图像
            annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)
            cv2.imshow("Camera", annotated_image)
    
        command_history.pop(0)
        command_history.append(command)
    
        # 连续frame_num 次相同的命令
        if len(set(command_history)) == 1:
            print(command)
        
        # 按下 'q' 键退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        # break
