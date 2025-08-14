# core/config.py

import os

# Жалпы конфигурация
ORG_NAME = "enu-ulk"
WINDOW_SIZE = "1200x668"
AUDIO_FOLDER = "/home/pi/Desktop/inclusive_guide/assets/audio"
MAP_FOLDER = "assets/maps"
RECOG_AUDIO_MODEL = "/home/pi/Desktop/inclusive_guide/models/vosk-model-small-kz-0.15"
FOR_RECOG_AUDIO = "/home/pi/Desktop/inclusive_guide/core/vosk/rec_audio.wav"
DATA_BASE="/home/pi/Desktop/inclusive_guide/core/db/enu_ulk/application.db"

# Лог деңгейі
LOGGING_LEVEL = "INFO"

# Камера конфигурациясы
CAMERA_RESOLUTION = (640, 640)
CAMERA_CONTROLS = {
    "AeEnable": False,
    "AnalogueGain": 4.0,
    "ExposureTime": 20000,
}

# Аудио файлдар үшін
FORWARD_AUDIO = "forward.mp3"
TURN_LEFT_AUDIO = "turn_left.mp3"
TURN_RIGHT_AUDIO = "turn-right.mp3"
GO_STRAIGHT_AUDIO = "go_straigth.mp3"
ROUTE_FOUND_AUDIO = "route_found.mp3"
NOT_RECOGNIZED_AUDIO = "not_recog.mp3"
INPUT_NUMBER_AUDIO = "input_need_number.mp3"
