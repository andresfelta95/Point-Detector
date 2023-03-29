from machine import Pin, ADC

class Mux: 

    def __init__(self, pin_s0, pin_s1, pin_s2, pin_s3, pin_e):
        self.pin_s0 = Pin(pin_s0, Pin.OUT)
        self.pin_s1 = Pin(pin_s1, Pin.OUT)
        self.pin_s2 = Pin(pin_s2, Pin.OUT)
        self.pin_s3 = Pin(pin_s3, Pin.OUT)
        self.pin_e = Pin(pin_e, Pin.OUT)
        self.pin_e.value(0)
    
    def set_channel(self, channel):
        self.pin_s0.value(channel & 0x1)
        self.pin_s1.value(channel & 0x2)
        self.pin_s2.value(channel & 0x4)
        self.pin_s3.value(channel & 0x8)
