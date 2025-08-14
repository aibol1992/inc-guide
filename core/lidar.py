import serial,os
import struct
import time
import numpy as np
import sounddevice as sd
from pydub import AudioSegment
from pydub.playback import play
import subprocess
from core.config import AUDIO_FOLDER

def beep_signal(frequency=1000, duration=0.5, volume=0.05):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = np.sin(2 * np.pi * frequency * t) * volume
    sd.play(wave, sample_rate)
    sd.wait()


def play_audio_sequence(audio_files):
   
    for audio_file in audio_files:
        audio_path = os.path.join(AUDIO_FOLDER, audio_file)
        if os.path.exists(audio_path):
            audio = AudioSegment.from_mp3(audio_path)
            
            # Аудионы `subprocess` арқылы ойнату (шығысты өшіру үшін)
            with subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", audio_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            ) as proc:
                proc.wait()  # Аудио аяқталғанша күту
        else:
            print(f"Файл табылған жоқ: {audio_path}")

def read_distance_from_lidar():
    port = "/dev/ttyAMA0"
    baudrate = 115200

    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            while True:
                count = ser.in_waiting
                if count > 8:
                    recv = ser.read(9)
                    ser.reset_input_buffer()

                    if recv[0] == 0x59 and recv[1] == 0x59:
                        distance = struct.unpack('<H', recv[2:4])[0]
                        strength = struct.unpack('<H', recv[4:6])[0]
                        
                        if distance < 30:
                            beep_signal(frequency=2000, duration=0.2)
                        elif 30 <= distance < 40:
                            beep_signal(frequency=1500, duration=0.5)
                        elif 40 < distance <= 50:
                            beep_signal(frequency=1000, duration=0.7)
                        elif 100>= distance >=90:
                            sounds = ["detected_barrier.mp3"]
                            play_audio_sequence(sounds)
                        time.sleep(0.1)
                        
    except serial.SerialException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read_distance_from_lidar()
