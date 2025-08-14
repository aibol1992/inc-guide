import numpy as np
import math
import pygame
import os
from pydub import AudioSegment
from pydub.playback import play
import subprocess
from core.config import AUDIO_FOLDER



def save_number_audio(number: int, output_path: str, folder_path: str = AUDIO_FOLDER):
    # 1-ден 1000-ға дейінгі сандарды құрау
    digits = []

    if number >= 100:
        hundreds = number // 100 * 100
        digits.append(f"{hundreds}_kz.mp3")
        number %= 100

    if number >= 10:
        tens = number // 10 * 10
        digits.append(f"{tens}_kz.mp3")
        number %= 10

    if number > 0:
        digits.append(f"{number}_kz.mp3")

    # Аудио біріктіру
    combined = AudioSegment.silent(duration=500)
    for filename in digits:
        path = os.path.join(folder_path, filename)
        if os.path.exists(path):
            combined += AudioSegment.from_file(path)
        else:
            print(f"Файл табылмады: {path}")

    combined.export(output_path, format="mp3")


def find_turns(path):
    reversed_path = path[::-1]
    turns = []  # turn coordinates
    directions = []  # turn left or right
    distances = []  # distance after turn
    total_distance = 0  # total length of route
    previous_direction = None
    min_distance_threshold = 5  # min distance for turn

    for i in range(1, len(reversed_path)):
        # start and end points
        (x1, y1) = reversed_path[i - 1]
        (x2, y2) = reversed_path[i]

        # find direction
        current_direction = (x2 - x1, y2 - y1)

        # if this is not the first step and direction changes
        if previous_direction is not None and current_direction != previous_direction:
            # if distance before and after direction is greater than minimum threshold
            if total_distance >= min_distance_threshold:
                # find direction of the turn (left or right)
                cross_product = previous_direction[0] * current_direction[1] - previous_direction[1] * current_direction[0]
                if cross_product > 0:
                    turn_direction = 'turn right'
                else:
                    turn_direction = 'turn left'

                # save turn place, write distance and turn
                turns.append(reversed_path[i - 1])
                directions.append(turn_direction)
                distances.append(total_distance)
            total_distance = 0  # reset distance calculation

        # calculate distance
        distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        total_distance += distance / 10

        # update previous direction
        previous_direction = current_direction

    # If no turns were found, use a smaller threshold and find the first turn
    first_turn_length = None
    first_turn_coords = None

    if path:
        min_distance_threshold = 1
        total_distance1 = 0
        previous_direction = None
        turns1=[]
        directions1=[]
        distances1=[]
        for i in range(1, len(reversed_path)):
            (x1, y1) = reversed_path[i - 1]
            (x2, y2) = reversed_path[i]
            current_direction = (x2 - x1, y2 - y1)

            if previous_direction is not None and current_direction != previous_direction:
                cross_product = previous_direction[0] * current_direction[1] - previous_direction[1] * current_direction[0]
                if cross_product > 0:
                    turn_direction1 = 'turn right'
                else:
                    turn_direction1 = 'turn left'

                turns1.append(reversed_path[i - 1])
                directions1.append(turn_direction1)
                distances1.append(total_distance1)
                first_turn_length = total_distance1
                first_turn_coords = reversed_path[i - 1]
                break  # stop after finding the first turn

            distance1 = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            total_distance1 += distance1 / 10
            previous_direction = current_direction

    return turns, directions, distances, first_turn_length, first_turn_coords,turn_direction1


def play_audio_sequence(audio_files, gain_increase=15):
    """
    Аудио файлдарды ойнатады. Егер файлдың аты "merged" сөзінен басталса, оны ойнатылғаннан кейін өшіреді.

    :param audio_files: Ойнатылатын аудио файлдардың тізімі.
    :param audio_folder: Аудио файлдар орналасқан папка.
    :param gain_increase: Дыбыс деңгейін арттыру (децибелмен).
    """
    for audio_file in audio_files:
        audio_path = os.path.join(AUDIO_FOLDER, audio_file)
        if os.path.exists(audio_path):
            print(f"Файл табылды: {audio_path}")  # Лог: Файл табылды
            try:
                # MP3 файлды жүктеу
                audio = AudioSegment.from_mp3(audio_path)
                #print(f"Файл жүктелді: {audio_file}")  # Лог: Файл жүктелді
                
                # Дыбыс деңгейін арттыру
                amplified_audio = audio + gain_increase
                
                # Уақытша файл жасау
                temp_path = "temp_amplified_audio.mp3"
                amplified_audio.export(temp_path, format="mp3")
                
                # Аудионы ойнату
                with subprocess.Popen(
                    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", temp_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                ) as proc:
                    proc.wait()  # Аудио аяқталғанша күту
                #print(f"Аудио ойнатылды: {audio_file}")  # Лог: Аудио ойнатылды
                
                # Уақытша файлды өшіру
                os.remove(temp_path)
                #print("Уақытша файл өшірілді.")  # Лог: Уақытша файл өшірілді
                
                audio_name=os.path.basename(audio_file)
                
                # Егер файлдың аты "merged" сөзінен басталса, оны өшіру
                if audio_name.startswith("merged"):
                    os.remove(audio_path)
                    #print(f"Файл өшірілді: {audio_name}")  # Лог: Файл өшірілді
            except Exception as e:
                print(f"Файлды өңдеу кезінде қате орын алды: {audio_path}\nҚате: {e}")
        else:
            print(f"Файл табылған жоқ: {audio_path}")    
