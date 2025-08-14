# core/light_control.py

import time
import threading
import board
import busio
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

class LightSensorContrast:
    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS1115(self.i2c)
        self.ads.gain = 1
        self.channel = AnalogIn(self.ads, 1)
        self.contrast = 1.0
        self.running = False

    def _calculate_contrast(self, voltage):
        if voltage < 0.5:
            return 2.5  
        elif voltage < 1.0:
            return 2.0
        elif voltage < 1.5:
            return 1.5
        elif voltage < 2.5:
            return 1.2
        else:
            return 1.0  

    def start_monitoring(self):
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        while self.running:
            voltage = self.channel.voltage
            self.contrast = self._calculate_contrast(voltage)
            time.sleep(0.2)

    def get_contrast(self):
        return self.contrast
