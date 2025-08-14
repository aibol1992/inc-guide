import cv2,numpy as np,os
import time
from typing import List
from core.audio import enqueue_audio_files
#from distance_to_camera import find_marker,distance_to_camera

# Object detection setup
KNOWN_DISTANCE = 60.96
KNOWN_WIDTH = 27.94
focalLength = 0.0

thres = 0.25
classNames = []
classFile = "models/coco.names"
with open(classFile, "rt") as f:
    classNames = f.read().rstrip("\n").split("\n")
   
configPath = "models/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "models/frozen_inference_graph.pb"

if not os.path.exists(weightsPath):
    print(f"Model weights file not found at {weightsPath}")
if not os.path.exists(configPath):
    print(f"Config file not found at {configPath}")

net = cv2.dnn_DetectionModel(weightsPath, configPath)

#net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(480, 240)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

#detect object
def getObjects(img, thres, nms, draw=True, objects=[]):
    global focalLength
    classIds, confs, bbox = net.detect(img, confThreshold=thres, nmsThreshold=nms)
    if len(objects) == 0: objects = classNames
    objectInfo = []
    distance = 0  
    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            className = classNames[classId - 1]
            if className in objects:                
                objectInfo.append([box, className,confidence])

            #marker = find_marker(img)
            #if marker is not None:
                #if focalLength == 0.0:
                    #focalLength = (marker[1][0] * KNOWN_DISTANCE) / KNOWN_WIDTH
                #distance = distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])
                #cv2.putText(img, f" Distance: {round(distance, 2)} cm", (box[0] + 10, box[1] + 60),
                 #           cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 2)
            else:
                print("Marker табылмады, қашықтықты есептеу мүмкін емес.")
              
    return img, objectInfo

def detect_rooms(image):
    # Суретті GRAYSCALE форматқа ауыстыру
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Бинаризация жасау
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)    
    rooms = {}
    room_id = 1  # Бөлмелерді нөмірлеу үшін
    
    for contour in contours:
        # Контурдың шекарасын алу
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Егер контур төртбұрыш болса
        if len(approx) == 4 and cv2.contourArea(contour) > 500:  # Төрт қабырға және минималды өлшем
            x, y, w, h = cv2.boundingRect(contour)            
           
            rooms[f"Room_{room_id}"] = (x + w // 2, y + h // 2)  # Бөлме ортасының координаттарын сақтау
            room_id += 1            
            
            cv2.rectangle(image, (x, y), (x + w, y + h), (60, 50, 255), 2)# Контурды суретке салу
    
    if not rooms:
        print("Бөлмелер табылмады!")
    #output_file = 'enhanced_img.png'
    #cv2.imwrite(output_file, image)
    return rooms, image


def add_object(obj_name: str, state) -> None:
    if any(obj['object'] == obj_name for obj in state.detected_objects):
        return

    warning_audio = {
        "person": "warning_front_person.mp3",
        "chair": "warning_front_chair.mp3",
        "table": "warning_front_table.mp3",
    }.get(obj_name)

    if warning_audio:
        enqueue_audio_files(state.audio_queue, [warning_audio])

    state.detected_objects.append({
        'object': obj_name,
        'time_added': time.time()
    })


def remove_expired_objects(state, expiry_seconds: int = 5):
    while True:
        current_time = time.time()
        state.detected_objects[:] = [
            obj for obj in state.detected_objects
            if current_time - obj['time_added'] < expiry_seconds
        ]
        time.sleep(1)

