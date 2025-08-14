# core/qr.py

from core.state import AppState
from core.audio import enqueue_audio_files
from core.db_handler import get_room_coordinates_from_db
from core.config import TURN_LEFT_AUDIO, TURN_RIGHT_AUDIO
from core.instructions import save_number_audio
import cv2
from pyzbar.pyzbar import decode

def decodeQR(img):
     # QR кодты іздеу үшін бейнені алдын ала өңдеу
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Грейскейлге айналдыру
    blurred_img = cv2.GaussianBlur(gray_img, (5, 5), 0)  # Шуды азайту
    enhanced_img = cv2.adaptiveThreshold(blurred_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 2)  # Контрастты арттыру
    #output_file = 'enhanced_img.png'
    #cv2.imwrite(output_file, enhanced_img)
    
    decoded_objects = decode(enhanced_img)
    qr_data = None 
    for obj in decoded_objects:
        points = obj.polygon
        if len(points) > 4:
            hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
            points = hull
        else:
            for j in range(len(points)):
                cv2.line(img, tuple(points[j]), tuple(points[(j+1) % len(points)]), (255, 0, 0), 3)
        x, y, w, h = obj.rect
        qr_data = obj.data.decode('utf-8')
        cv2.putText(img, qr_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        # print("Data:", qr_data)
    return img, qr_data


def handle_qr_detection(app, qr_room: str, state: AppState):
    try:
        if not qr_room:
            return

        if qr_room in state.detected_room_qr:
            return

        state.detected_room_qr.append(qr_room)

        if qr_room == "left":
            enqueue_audio_files(state.audio_queue, [TURN_LEFT_AUDIO])
            return
        elif qr_room == "right":
            enqueue_audio_files(state.audio_queue, [TURN_RIGHT_AUDIO])
            return

        if state.target_room == qr_room:
            enqueue_audio_files(state.audio_queue, ["0_kz.mp3"])
            state.reset()
            return

        qr_coords = get_room_coordinates_from_db(qr_room, sequence=None, state=state)

        if not state.another_floor:
            if len(state.detected_room_qr) == 1:
                state.floor = get_floor_from_room_number(qr_room)
                if qr_room.isdigit():
                    save_number_audio(int(qr_room), "assets/audio/output_digital.mp3")
                    enqueue_audio_files(state.audio_queue, ["output_digital.mp3", "input_need_number.mp3"])
            else:
                if qr_room.isdigit():
                    save_number_audio(int(qr_room), "assets/audio/output_digital3.mp3")
                    enqueue_audio_files(state.audio_queue, ["output_digital3.mp3"])
                app.update_route(qr_room, state.target_room)
        else:
            app.update_route(qr_room, state.target_room)
            state.another_floor = False

    except Exception as e:
        print(f"QR өңдеу кезінде қате: {e}")


def get_floor_from_room_number(room_number: str) -> int:
    try:
        num = int(room_number)
        if (99 < num <= 200) or (num == 1):
            return 1
        elif (199 < num <= 300) or (num == 2):
            return 2
        elif (299 < num <= 400) or (num == 3):
            return 3
        else:
            return 0
    except ValueError:
        print(f"Қате: {room_number} бүтін санға түрленбейді!")
        return 0
