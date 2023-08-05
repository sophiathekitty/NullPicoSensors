import machine

class motion():
    # Connect the motion sensor to GPIO pin ie: 1 for GP1
    def __init__(self,pin):
        print(f"add motion sensor on pin: {pin}")
        self.gpio = pin
        self.motion_sensor = machine.Pin(pin, machine.Pin.IN)
        self.level = 0

    def read_sensor(self):
        if self.motion_sensor.value() == 1:  # Motion detected (sensor output is high)
            self.level += 1
            if self.level == 1:
                return True
        return False
    # get the json
    def get_json(self,mac_address):
        data = {
            'mac_address' : mac_address,
            'gpio' : self.gpio,
            'level' : self.level
        }
        return data
    # resets the min and max values
    def reset_min_max(self):
        self.level = 0
