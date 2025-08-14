# core/db_handler.py

import sqlite3
from core.state import AppState
from core.config import DATA_BASE
from typing import Optional, Tuple


def get_map(org_name, floor):
    import sqlite3
    connection = sqlite3.connect(DATA_BASE)
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT m.name FROM organizations o LEFT JOIN maps m ON o.org_id = m.org_id WHERE o.name = ? AND m.floor_id = ?",
            (org_name, floor or 1),
        )
        result = cursor.fetchone()
        if result:
            return f"assets/maps/{result[0]}"
    finally:
        connection.close()
    return ""

def get_room_coordinates_from_db(qr_room: str, sequence: Optional[str], state: AppState) -> Optional[Tuple[int, int]]:
    try:
        map_name = state.map_path.split("/")[-1]
        connection = sqlite3.connect(DATA_BASE)
        cursor = connection.cursor()

        query = (
            "SELECT c.x, c.y, direction FROM coordinates c "
            "LEFT JOIN maps m ON m.id = c.map_id "
            "WHERE m.name = ? AND c.room_number = ?"
        )
        cursor.execute(query, (map_name, qr_room))
        result = cursor.fetchone()

        if result:
            x, y, direction = result
            if sequence == "first":
                state.qr_direction = direction
            return int(x), int(y)

        # Try searching in other floors
        cursor.execute(
            "SELECT m.name, m.floor_id FROM maps m "
            "LEFT JOIN organizations o ON o.org_id = m.org_id WHERE o.name = ?",
            (state.org_name,)
        )
        maps = cursor.fetchall()

        for other_map_name, map_floor in maps:
            if other_map_name != map_name:
                cursor.execute(query, (other_map_name, qr_room))
                result = cursor.fetchone()
                if result:
                    x, y, direction = result
                    if sequence == "first":
                        state.qr_direction = direction
                    state.map_path = f"assets/maps/{other_map_name}"
                    if state.floor != map_floor:
                        if len(state.detected_room_qr) != 1:
                            state.another_floor = True
                        state.floor = map_floor
                    return int(x), int(y)

        print(f"Бөлме {qr_room} координаттары табылмады.")
        return None

    except sqlite3.Error as e:
        print(f"Дерекқор қатесі: {e}")
        return None

    finally:
        if 'connection' in locals() and connection:
            connection.close()
