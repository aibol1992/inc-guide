from gpiozero import Button
import subprocess
import time
from recog import recognation

BUTTON_PIN = 18  # GPIO пинінің нөмірі

# Button объектісін орнату
button = Button(BUTTON_PIN, pull_up=True)

try:
    print("Аудио жазу үшін кнопканы басып тұрыңыз.")
    while True:
        if button.is_pressed:  # Кнопка басылғанда
            print("Жазу басталды...")
            # Дыбысты жазу
            process = subprocess.Popen(["arecord", "-D", "plughw:2,0", "-f", "S16_LE", "-r", "16000", "-d", "0", "test.wav"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # Кнопка босатылғанша күту
            button.wait_for_release()
            process.terminate()  # Процесті тоқтату
            
            print("Жазу аяқталды.")
            recognation()
        time.sleep(0.1)
    
except KeyboardInterrupt:
    print("Бағдарлама тоқтатылды.")
