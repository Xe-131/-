import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import cv2

import math
from enum import Enum, auto

# 定义手势枚举
class GestureOneHand(Enum):
    NONE = auto()
    TWO = auto()
    THREE = auto()
    FOUR = auto()
    # 手背在后
    FIVE_FORWARD = auto()
    # 手心在后
    FIVE_BACKWARD = auto()
    SEVEN = auto()
    OK = auto()
    GOOD = auto()
    BAD = auto()
# 定义命令枚举   
class FlyCommand(Enum):
    NONE = auto()
    TAKE_OFF = auto()
    LAND = auto()
    MOVE_RIGHT = auto()
    MOVE_LEFT = auto()
    MOVE_FORWARD = auto()
    MOVE_BACKWARD = auto()
    YOW_LEFT = auto()
    YOW_RIGHT = auto()



# 图片大小
img_width = 720
img_height = 640 


MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54) # vibrant green

"""
输入RGB 的numpy array 和 识别结果对象
输出将键点和连线标注好的RGB 图片
"""
def draw_landmarks_on_image(rgb_image, detection_result):
  hand_landmarks_list = detection_result.hand_landmarks
  handedness_list = detection_result.handedness
  annotated_image = np.copy(rgb_image)

  # Loop through the detected hands to visualize.
  for idx in range(len(hand_landmarks_list)):
    hand_landmarks = hand_landmarks_list[idx]
    handedness = handedness_list[idx]

    # Draw the hand landmarks.
    hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    hand_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
    ])
    solutions.drawing_utils.draw_landmarks(
      annotated_image,
      hand_landmarks_proto,
      solutions.hands.HAND_CONNECTIONS,
      solutions.drawing_styles.get_default_hand_landmarks_style(),
      solutions.drawing_styles.get_default_hand_connections_style())

    # Get the top left corner of the detected hand's bounding box.
    height, width, _ = annotated_image.shape
    x_coordinates = [landmark.x for landmark in hand_landmarks]
    y_coordinates = [landmark.y for landmark in hand_landmarks]
    text_x = int(min(x_coordinates) * width)
    text_y = int(min(y_coordinates) * height) - MARGIN

    # Draw handedness (left or right hand) on the image.
    cv2.putText(annotated_image, f"{handedness[0].category_name}",
                (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)
   
    # Add numbering to the landmarks
    for i, landmark in enumerate(hand_landmarks):
        # Convert the normalized coordinates to pixel values
        landmark_x = int(landmark.x * width)
        landmark_y = int(landmark.y * height)
    
        # Draw the point number next to each landmark
        cv2.putText(annotated_image, str(i), (landmark_x + 5, landmark_y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)

    # 画出多边形 
    connection_indices = [0, 1, 2, 3, 6, 10, 14, 19, 18, 17, 0]  # Define the indices to connect
    # 在17 这个点上的多边形部分向下移动，方便识别小拇指弯曲
    # hand_landmarks[17].y = hand_landmarks[17].y + 0.1
    for i in range(len(connection_indices) - 1):
        start_idx = connection_indices[i]
        end_idx = connection_indices[i + 1]

        start_landmark = hand_landmarks[start_idx]
        end_landmark = hand_landmarks[end_idx]

        # Convert normalized coordinates to pixel values
        start_x = int(start_landmark.x * width)
        start_y = int(start_landmark.y * height)
        end_x = int(end_landmark.x * width)
        end_y = int(end_landmark.y * height)
        
        # Draw a line between the landmarks
        cv2.line(annotated_image, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)       

    # 指定位置添加文字
#     x = 0.75
#     y = 0.1
#     for state in finger_state:
#         # 伸直 
#         if state:
#             text = "unbend"
#         else:
#             text = "bend"
# 
#         put_text(annotated_image, text, x, y)
#         y = y + 0.05

  return annotated_image
"""
cv2.putText 函数预设格式
"""
def put_text(img, text, x, y):
    position = (int(x*img_width), int(y*img_height))
    font_size = 1
    thickness = 2

    cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 255, 255), thickness, cv2.LINE_AA)


"""
计算A, B之间的距离：L2距离（欧式距离）
输入为关键点对象
"""
def points_distance(A, B):
    # 换算真实坐标
    A_x = A.x * img_width
    A_y = A.y * img_height
    B_x = B.x * img_width
    B_y = B.y * img_height

    return math.sqrt((A_x - B_x) ** 2 + (A_y - B_y) ** 2)

"""
计算向量AB, CD 的夹角，以角度表示
输入为关键点对象
"""
def compute_angle(A, B, C, D):
    # 换算真实坐标
    A_x = A.x * img_width
    A_y = A.y * img_height
    B_x = B.x * img_width
    B_y = B.y * img_height
    C_x = C.x * img_width
    C_y = C.y * img_height
    D_x = D.x * img_width
    D_y = D.y * img_height

    AB = [A_x - B_x, A_y - B_y]
    CD = [C_x - D_x, C_y - D_y]

    dot_product = AB[0] * CD[0] + AB[1] * CD[1]

    AB_distance = points_distance(A, B) + 0.001   # 防止分母出现0
    CD_distance = points_distance(C, D) + 0.001

    cos_theta = dot_product / (AB_distance * CD_distance)

    theta = math.acos(cos_theta)

    return theta * (180/math.pi)

"""
判断给定的点是否在由指定关键点索引构成的多边形内部（使用射线法）

输入为特定手掌的的关键点对象列表
:param detect_result: 包含所有关键点的列表，每个点具有 .x 和 .y 属性，表示归一化坐标
:param point_index: 要检测的点在 detect_result 中的索引
:return: 如果点在多边形内部，返回 True；否则返回 False。
"""
def is_point_in_polygon(detect_result, point_index):
    # 将17 向下移动一些距离，方便判断小拇指弯曲
    # detect_result[17].y = detect_result[17].y + 0.1

    # 多边形顶点索引
    polygon_indices = [0, 1, 2, 3, 6, 10, 14, 19, 18, 17, 0]
    # 获取待检测的点
    point = detect_result[point_index]
    px = int(point.x * img_width)
    py = int(point.y * img_height)
    
    # 根据 polygon_indices 构建多边形的顶点列表
    polygon = [(int(detect_result[i].x * img_width), int(detect_result[i].y * img_height)) for i in polygon_indices]

    # 计算交点数
    num_intersections = 0
    n = len(polygon)
    
    for i in range(n):
        # 获取多边形的边
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]  # 循环回到起点
        
        # 判断射线是否与当前边相交
        if (y1 > py) != (y2 > py):  # 点在射线的y范围内
            # 计算边与水平射线的交点
            x_intersection = (py - y1) * (x2 - x1) / (y2 - y1) + x1
            if x_intersection > px:
                num_intersections += 1
    
    # 如果交点数是奇数，点在多边形内；如果是偶数，点在多边形外
    return num_intersections % 2 == 1

"""
判断各个手指弯曲情况、

输入为特定手掌的的关键点对象列表
输出从大拇指到小指顺序排列的01列表，1代表伸直
"""
def is_finger_bend(detection_result):
    # detection_result_copy = detection_result

    # 各个手指顶点
    point_list = [4, 8, 12, 16, 20]
    # 弯曲伸直状态
    state = []
    
    for point_index in point_list:
        if is_point_in_polygon(detection_result, point_index):
            state.append(0)
        else:
            state.append(1)

    return state

"""
获取单手势
输入：单个手掌关键点对象列表，单个手掌手指状态伸直列表, 手掌类型
输出：手掌手势枚举变量
"""
def get_gesture_onehand(detect_result, finger_state, handedness):

    if handedness == "Right":
    
        gesture = GestureOneHand.NONE
        if (finger_state[0] == 0 and finger_state[1] == 1 and  finger_state[2] == 1 and finger_state[3] == 0):
            gesture = GestureOneHand.TWO
        # 4 18 距离小于 5 6
        elif (finger_state[0] == 0 and finger_state[1] == 1 and  finger_state[2] == 1 and finger_state[3] == 1 and finger_state[4] == 0) and (points_distance(detect_result[4], detect_result[18]) < points_distance(detect_result[5], detect_result[6])):
            gesture = GestureOneHand.THREE
        elif (finger_state[0] == 0 and finger_state[1] == 1 and  finger_state[2] == 1 and finger_state[3] == 1 and finger_state[4] == 1):
            gesture = GestureOneHand.FOUR
        # 4 8 距离小于 2 3
        elif (finger_state[0] == 1 and finger_state[1] == 1 and  finger_state[2] == 1 and finger_state[3] == 1 and finger_state[4] == 1) and (points_distance(detect_result[4], detect_result[8]) > points_distance(detect_result[2], detect_result[3])):
            # 手背在后(4 在 20 右边)
            if detect_result[4].x > detect_result[20].x:
                gesture = GestureOneHand.FIVE_FORWARD
            # 手心在后(4 在 20 左边)
            else:
                gesture = GestureOneHand.FIVE_BACKWARD
        elif (finger_state[0] == 1 and finger_state[1] == 1 and  finger_state[2] == 0 and finger_state[3] == 0 and finger_state[4] == 0):
            gesture = GestureOneHand.SEVEN
        # 4 高于 17
        elif (finger_state[0] == 1 and finger_state[1] == 0 and  finger_state[2] == 0 and finger_state[3] == 0 and finger_state[4] == 0) and (detect_result[4].y < detect_result[17].y):
            gesture = GestureOneHand.GOOD
        # 4 低于 17
        elif (finger_state[0] == 1 and finger_state[1] == 0 and  finger_state[2] == 0 and finger_state[3] == 0 and finger_state[4] == 0) and (detect_result[4].y > detect_result[17].y):
            gesture = GestureOneHand.BAD
        elif (finger_state[2] == 1 and finger_state[3] == 1 and finger_state[4] == 1):
            # 4 8 距离小于 2 3
            if points_distance(detect_result[4], detect_result[8]) < points_distance(detect_result[2], detect_result[3]):
                gesture = GestureOneHand.OK

    elif handedness == "Left":

        gesture = GestureOneHand.NONE
        if (finger_state[0] == 0 and finger_state[1] == 1 and  finger_state[2] == 1 and finger_state[3] == 0):
            gesture = GestureOneHand.TWO
        # 4 18 距离小于 5 6
        elif (finger_state[0] == 0 and finger_state[1] == 1 and  finger_state[2] == 1 and finger_state[3] == 1 and finger_state[4] == 0) and (points_distance(detect_result[4], detect_result[18]) < points_distance(detect_result[5], detect_result[6])):
            gesture = GestureOneHand.THREE
        elif (finger_state[0] == 0 and finger_state[1] == 1 and  finger_state[2] == 1 and finger_state[3] == 1 and finger_state[4] == 1):
            gesture = GestureOneHand.FOUR
        # 4 8 距离小于 2 3
        elif (finger_state[0] == 1 and finger_state[1] == 1 and  finger_state[2] == 1 and finger_state[3] == 1 and finger_state[4] == 1) and (points_distance(detect_result[4], detect_result[8]) > points_distance(detect_result[2], detect_result[3])):
            # 手背在后(20 在 4 右边)
            if detect_result[4].x < detect_result[20].x:
                gesture = GestureOneHand.FIVE_FORWARD
            # 手心在后(20 在 4 左边)
            else:
                gesture = GestureOneHand.FIVE_BACKWARD
        elif (finger_state[0] == 1 and finger_state[1] == 1 and  finger_state[2] == 0 and finger_state[3] == 0 and finger_state[4] == 0):
            gesture = GestureOneHand.SEVEN
        # 4 高于 17
        elif (finger_state[0] == 1 and finger_state[1] == 0 and  finger_state[2] == 0 and finger_state[3] == 0 and finger_state[4] == 0) and (detect_result[4].y < detect_result[17].y):
            gesture = GestureOneHand.GOOD
        # 4 低于 17
        elif (finger_state[0] == 1 and finger_state[1] == 0 and  finger_state[2] == 0 and finger_state[3] == 0 and finger_state[4] == 0) and (detect_result[4].y > detect_result[17].y):
            gesture = GestureOneHand.BAD
        elif (finger_state[2] == 1 and finger_state[3] == 1 and finger_state[4] == 1):
            # 4 8 距离小于 2 3
            if points_distance(detect_result[4], detect_result[8]) < points_distance(detect_result[2], detect_result[3]):
                gesture = GestureOneHand.OK
        
    return gesture

"""
根据双手的手势判断具体指令
输入：双手的手势枚举
输出：具体指令的枚举
注：这里的左右是我面对屏幕时，我的自己的左右
"""
def get_command(gesture_left, gesture_right):

    command = FlyCommand.NONE
    if gesture_left == GestureOneHand.SEVEN and gesture_right == GestureOneHand.FIVE_FORWARD:
        command = FlyCommand.MOVE_RIGHT
    elif gesture_left == GestureOneHand.FIVE_FORWARD and gesture_right == GestureOneHand.SEVEN:
        command = FlyCommand.MOVE_LEFT
    elif gesture_left == GestureOneHand.GOOD and gesture_right == GestureOneHand.GOOD:
        command = FlyCommand.TAKE_OFF
    elif gesture_left == GestureOneHand.BAD and gesture_right == GestureOneHand.BAD:
        command = FlyCommand.LAND
    elif gesture_left == GestureOneHand.FIVE_FORWARD and gesture_right == GestureOneHand.FIVE_FORWARD:
        command = FlyCommand.MOVE_FORWARD
    elif gesture_left == GestureOneHand.FIVE_BACKWARD and gesture_right == GestureOneHand.FIVE_BACKWARD:
        command = FlyCommand.MOVE_BACKWARD
    elif gesture_left == GestureOneHand.OK  and gesture_right == GestureOneHand.SEVEN:
        command = FlyCommand.YOW_LEFT
    elif gesture_left == GestureOneHand.SEVEN  and gesture_right == GestureOneHand.OK:
        command = FlyCommand.YOW_RIGHT


    return command
