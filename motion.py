import machine
from picozero import pico_led

class motion():
    # Connect the motion sensor to GPIO pin ie: 1 for GP1
    def __init__(self,pin,remote_id,name,mac_address,report_threshold=1):
        print(f"add motion sensor on pin: {pin} remote_id: {remote_id} name: {name} mac_address: {mac_address}")
        self.gpio = pin
        self.remote_id = remote_id
        self.name = name
        self.mac_address = mac_address
        self.motion_sensor = machine.Pin(pin, machine.Pin.IN)
        self.level = 0
        self.report = 0
        self.reported = False
        self.report_threshold = report_threshold
        self.show = False
        
    def read_sensor(self):
        if self.motion_sensor.value() == 1:  # Motion detected (sensor output is high)
            if self.show:
                pico_led.on()
            self.level += 1
            self.report += 1
            if self.report == self.report_threshold:
                self.reported = True
                return True
        elif self.show:
            self.report -= 1
            if self.report < 0:
                self.reported = False
                self.report = 0
            pico_led.off()
        return False
    # get the json
    def get_json(self):
        data = {
            'id' : self.remote_id,
            'remote_id' : self.remote_id,
            'name' : self.name,
            'mac_address' : self.mac_address,
            'gpio' : self.gpio,
            'level' : self.level
        }
        return data
    # resets the min and max values
    def reset_min_max(self):
        self.level = 0