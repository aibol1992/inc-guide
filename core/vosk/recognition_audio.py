import subprocess,time,wave,json,re,sys,os,pygame
from gpiozero import Button
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
from queue import Queue
from pydub.playback import play
from core.config import AUDIO_FOLDER,RECOG_AUDIO_MODEL,FOR_RECOG_AUDIO

def play_audio_sequence(audio_files, playback_speed=1.0):
    """
    Кезекпен аудио файлдарды ойнату.
    :param audio_files: Ойнатылатын аудио файлдардың тізімі
    :param playback_speed: Аудионың ойнату жылдамдығы (1.0 - қалыпты, 1.5 - 1.5 есе тез)
    """
    for audio_file in audio_files:
        audio_path = os.path.join(AUDIO_FOLDER, audio_file)
        if os.path.exists(audio_path):
            audio = AudioSegment.from_mp3(audio_path)
            audio = audio.speedup(playback_speed=playback_speed)
            play(audio)
        else:
            print(f"Файл табылған жоқ: {audio_path}")

BUTTON_PIN = 18
button = Button(BUTTON_PIN, pull_up=True)

# kazakh dictionary
numbers_dict = {
    "нөл": 0, "бір": 1, "екі": 2, "үш": 3, "төрт": 4, "бес": 5, "алты": 6, "жеті": 7, "сегіз": 8, "тоғыз": 9,
    "он": 10, "жиырма": 20, "отыз": 30, "қырық": 40, "елу": 50, "алпыс": 60, "жетпіс": 70, "сексен": 80, "тоқсан": 90,
    "жүз": 100, "мың": 1000
}

# text digit to digital 
def text_to_number(text):
    words = text.split()
    total = 0
    current_number = 0
    
    for word in words:
        if word in numbers_dict:
            if word == "жүз":
                current_number = (current_number or 1) * 100
            elif word == "мың":
                current_number = (current_number or 1) * 1000
                total += current_number
                current_number = 0
            else:
                current_number += numbers_dict[word]
        else:
            total += current_number
            current_number = 0
    return total + current_number

# find digital in text 
def find_numbers_in_text(text):
    san_sandar = re.findall(r'нөл|бір|екі|үш|төрт|бес|алты|жеті|сегіз|тоғыз|он|жиырма|отыз|қырық|елу|алпыс|жетпіс|сексен|тоқсан|жүз|мың', text)
    if san_sandar:
        san_text = ' '.join(san_sandar)
        room_number = text_to_number(san_text)
        return room_number
    return None

def convert_audio_format(input_file, output_file):
    audio = AudioSegment.from_file(input_file)
    audio = audio.set_channels(1).set_sample_width(2).set_frame_rate(16000)
    audio.export(output_file, format="wav")

# audio to text
def recognize_speech(model_path, audio_file):
    model = Model(model_path)
    converted_audio_filename = "converted_audio_file.wav"
    
    with wave.open(audio_file, "rb") as wf:
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000]:
            convert_audio_format(audio_file, converted_audio_filename)
        else:
            converted_audio_filename = audio_file

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

    return result_text

# reconition audio
def recognize_and_enqueue(queue):
  
    
    try:
        print("Аудио жазу үшін кнопканы басып тұрыңыз.")
        while True:
            if button.is_pressed:
                sounds = ["record_run.mp3"]
                play_audio_sequence(sounds)
                print("Жазу басталды...")
                                
                process = subprocess.Popen(["arecord", "-D", "plughw:2,0", "-f", "S16_LE", "-r", "16000", "-d", "0",FOR_RECOG_AUDIO ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                button.wait_for_release()
                process.terminate()
                sounds = ["end_record.mp3"]
                play_audio_sequence(sounds)
                print("Жазу аяқталды.")

                recognized_text = recognize_speech(RECOG_AUDIO_MODEL, FOR_RECOG_AUDIO)
                print(f"Танылған мәтін: {recognized_text}")

                room_number = find_numbers_in_text(recognized_text)
                if room_number:
                    queue.put(room_number)
                    print(f"Табылған сан: {room_number}")
                else: 
                    room_number=-1
                    queue.put(room_number)                   
                    print("Сан табылған жоқ.")
                    
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Бағдарлама тоқтатылды.")
