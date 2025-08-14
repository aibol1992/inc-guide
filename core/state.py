# core/state.py

from queue import Queue
from typing import Optional

class AppState:
    def __init__(self):
        self.org_name: str = "enu-ulk"
        self.floor: int = 0
        self.target_floor: int = 0
        self.map_path: str = ""
        self.audio_files: list[str] = []
        self.road_traveled: list[str] = []
        self.detected_room_qr: list[str] = []
        self.turns: list[str] = []
        self.detected_objects: list[dict] = []
        self.qr_direction: Optional[str] = None
        self.target_room: Optional[str] = None

        self.number_queue: Queue = Queue()
        self.audio_queue: Queue = Queue()

        self.another_floor: bool = False
        self.height: int = 0

    def reset(self):
        self.floor = 0
        self.target_floor = 0
        self.map_path = ""
        self.audio_files.clear()
        self.road_traveled.clear()
        self.detected_room_qr.clear()
        self.turns.clear()
        self.detected_objects.clear()
        self.qr_direction = None
        self.target_room = None
        self.another_floor = False
