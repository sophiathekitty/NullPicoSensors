import machine
# class for handling a light sensor
class light():
    # Connect the analog light sensor to GPIO pin ie: 27 for GP27 (ADC1)
    def __init__(self,pin,remote_id,name,mac_address):
        print(f"add light sensor on pin: {pin}")
        self.gpio = pin
        self.remote_id = remote_id
        self.name = name
        self.mac_address = mac_address
        # light sensor
        self.ldr = machine.ADC(pin)
        self.level = None
        self.min = None
        self.max = None
    # read the sensor
    def read_sensor(self):
        self.level = self.ldr.read_u16()
        #min hum
        if self.min is None or self.level < self.min:
            self.min = self.level
        #max hum
        if self.max is None or self.level > self.max:
            self.max = self.level
    # get the json
    def get_json(self):
        data = {
            'id' : self.remote_id,
            'remote_id' : self.remote_id,
            'mac_address' : self.mac_address,
            'name' : self.name,
            'gpio' : self.gpio,
            'level' : self.level,
            'max' : self.max,
            'min' : self.min
        }
        return data
    # resets the min and max values
    def reset_min_max(self):
        self.max = None
        self.min = None
