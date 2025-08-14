# core/image.py

import cv2
import os
from core.state import AppState


def load_and_preprocess_map(state: AppState):
    if not os.path.exists(state.map_path):
        raise FileNotFoundError(f"Карта табылмады: {state.map_path}")

    image = cv2.imread(state.map_path, cv2.IMREAD_COLOR)
    scale_percent = 100
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)

    resized_image = cv2.resize(image, dim)
    state.height = resized_image.shape[0]

    gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blur, 128, 255, cv2.THRESH_BINARY_INV)

    # Қызыл түсті кедергілер ретінде
    obstacles = cv2.inRange(resized_image, (200, 0, 0), (255, 50, 50))
    # Ақ түсті жолдар ретінде
    paths = cv2.inRange(resized_image, (200, 200, 200), (255, 255, 255))

    return resized_image, obstacles, paths


def preprocess_image_for_display(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    processed_image = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    return processed_image


def save_annotated_map(image, path='annotated_map.png'):
    cv2.imwrite(path, image)
    return path
