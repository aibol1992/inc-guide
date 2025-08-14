# core/audio.py

import os
import time
from pydub import AudioSegment
from core.config import AUDIO_FOLDER
from typing import List

from core.instructions import play_audio_sequence


def merge_audio_files(file_list: List[str], folder_path: str = AUDIO_FOLDER) -> str:
    if not file_list:
        raise ValueError("Аудио файл тізімі бос болмауы керек.")

    file_paths = [os.path.join(folder_path, file) for file in file_list]
    if not all(os.path.exists(file) for file in file_paths):
        raise FileNotFoundError("Кейбір файлдар табылмады.")

    merged_file_name = "merged_" + "_".join([os.path.splitext(f)[0] for f in file_list]) + ".mp3"
    output_path = os.path.join(folder_path, merged_file_name)

    combined = AudioSegment.from_file(file_paths[0])
    for file in file_paths[1:]:
        combined += AudioSegment.from_file(file)

    combined.export(output_path, format="mp3")
    return output_path


def enqueue_audio_files(audio_queue, files: List[str]):
    if len(files) == 1:
        for file in files:
            audio_queue.put(file)
    else:
        merged_audio = merge_audio_files(files)
        audio_queue.put(merged_audio)


def audio_player(audio_queue):
    while True:
        if not audio_queue.empty():
            audio_file = audio_queue.get()
            play_audio_sequence([audio_file])
            audio_queue.task_done()
        else:
            time.sleep(0.1)
