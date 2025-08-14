# main.py

import tkinter as tk
import threading
from queue import Queue
from PIL import Image, ImageTk
import cv2
from core.state import AppState
from core.config import WINDOW_SIZE, ORG_NAME,CAMERA_CONTROLS
from core.object_ident import add_object, remove_expired_objects
from core.audio import audio_player, enqueue_audio_files
from core.image import load_and_preprocess_map, save_annotated_map
from core.vosk.recognition_audio import recognize_and_enqueue
from core.qr_handler import decodeQR,handle_qr_detection
from core.object_ident import getObjects
from core.route import a_star
from core.instructions import save_number_audio
from core.lidar import read_distance_from_lidar
from core.db_handler import get_map, get_room_coordinates_from_db


class RouteFinderApp(tk.Tk):
    def __init__(self, state: AppState):
        super().__init__()
        self.state = state
        self.title("Inclusive Guide")
        self.geometry(WINDOW_SIZE)

        self.image_queue = Queue()
        self.target_room = None

        self.map_label = tk.Label(self)
        self.map_label.grid(row=0, column=0, rowspan=7, padx=1, pady=1, sticky="nsew")

        self.camera_label = tk.Label(self)
        self.camera_label.grid(row=0, column=1)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.after(100, self.check_for_target_room)
        self.update_camera_image()

    def update_image(self, path):
        img = Image.open(path)
        img_tk = ImageTk.PhotoImage(img)
        self.map_label.config(image=img_tk)
        self.map_label.image = img_tk

    def update_camera_image(self):
        if not self.image_queue.empty():
            img_tk = self.image_queue.get()
            self.camera_label.config(image=img_tk)
            self.camera_label.image = img_tk
        self.after(10, self.update_camera_image)

    def check_for_target_room(self):
        if not self.state.number_queue.empty():
            room_number = self.state.number_queue.get()
            self.target_room = str(room_number)
            self.state.target_room = str(room_number)
            save_number_audio(int(room_number), "assets/audio/output_digital1.mp3")
            enqueue_audio_files(self.state.audio_queue, ["input_cabinet_number.mp3", "output_digital1.mp3"])

            if self.state.detected_room_qr:
                self.update_route(self.state.detected_room_qr[0], self.target_room)

        self.after(100, self.check_for_target_room)

    def update_route(self, qr_room, target_room):
        
        self.state.map_path = get_map(ORG_NAME, self.state.floor)
        image, obstacles, paths = load_and_preprocess_map(self.state)
        start = get_room_coordinates_from_db(qr_room, "first", self.state)

        if self.state.floor != self.state.target_floor:
            end = get_room_coordinates_from_db("ladder", "second", self.state)
        else:
            end = get_room_coordinates_from_db(target_room, "second", self.state)

        path = a_star(start, end, obstacles, paths)

        if path:
            for i in range(len(path) - 1):
                cv2.line(image, path[i], path[i + 1], (0, 255, 0), thickness=2)
            output_path = save_annotated_map(image)
            self.update_image(output_path)


def process_camera_feed(app: RouteFinderApp, state: AppState):
    from picamera2 import Picamera2
    from core.light_control import LightSensorContrast

    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"size": (640, 640)}))
    picam2.set_controls(CAMERA_CONTROLS)
    picam2.start()
    
    light_sensor = LightSensorContrast()
    light_sensor.start_monitoring()

    while True:
        contrast = light_sensor.get_contrast()
        picam2.set_controls({"Contrast": contrast})
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        _, qr_room = decodeQR(frame)
        if qr_room:
            threading.Thread(target=handle_qr_detection, args=(app, qr_room, state), daemon=True).start()

        _, objects = getObjects(frame, 0.6, 0.2, draw=True)
        for box, class_name, _ in objects:
            add_object(class_name, state)
            cv2.rectangle(frame, box, color=(0, 255, 0), thickness=2)
            cv2.putText(frame, class_name.upper(), (box[0] + 10, box[1] + 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

        img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img_tk = ImageTk.PhotoImage(image=img_pil)
        app.image_queue.put(img_tk)


if __name__ == "__main__":
    state = AppState()
    app = RouteFinderApp(state)

    threading.Thread(target=recognize_and_enqueue, args=(state.number_queue,), daemon=True).start()
    threading.Thread(target=audio_player, args=(state.audio_queue,), daemon=True).start()
    threading.Thread(target=remove_expired_objects, args=(state,), daemon=True).start()
    threading.Thread(target=process_camera_feed, args=(app, state), daemon=True).start()
    threading.Thread(target=read_distance_from_lidar, daemon=True).start()

    enqueue_audio_files(state.audio_queue, ["gid_run_read_start_qr.mp3"])
    app.mainloop()
