import wave
import json
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment

def convert_audio_format(input_file, output_file):
    audio = AudioSegment.from_file(input_file)
    audio = audio.set_channels(1).set_sample_width(2).set_frame_rate(16000)
    audio.export(output_file, format="wav")

# Қазақ тілі үлгісінің жолын көрсетіңіз
model_path = "/home/pi/Desktop/inclusive_guide_v3/models/vosk-model-small-kz-0.15"  # Бұл жерде сіз жүктеген үлгі жолын көрсетіңіз
model = Model(model_path)

# Аудио файлының атын көрсетіңіз
input_audio_filename = "test.wav"
converted_audio_filename = "converted_audio_file.wav"

def recognation():
    print("recognation started... ")
    # Файлды қажет форматқа түрлендіру
    with wave.open(input_audio_filename, "rb") as wf:
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000]:
            convert_audio_format(input_audio_filename, converted_audio_filename)
        else:
            converted_audio_filename = input_audio_filename

    # Түрлендірілген аудио файлын мәтінге айналдыру
    with wave.open(converted_audio_filename, "rb") as wf:
        recognizer = KaldiRecognizer(model, wf.getframerate())
        recognizer.SetWords(True)

        result_text = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                result_text += result.get("text", "") + " "

        final_result = json.loads(recognizer.FinalResult())
        result_text += final_result.get("text", "")

    # Нәтижені басып шығару
    print("Танылған мәтін:", result_text)
