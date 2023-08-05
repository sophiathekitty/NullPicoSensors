import dht
import machine


class temperature():
    # Connect the DHT11 sensor to GPIO pin ie: 2 for GP2
    def __init__(self,pin):
        print(f"add dht11 on pin: {pin}")
        self.gpio = pin
        self.dht_pin = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.dht_sensor = dht.DHT11(self.dht_pin)
        self.temp = None
        self.temp_min = None
        self.temp_max = None
        self.hum = None
        self.hum_min = None
        self.hum_max = None

    def celsius_to_fahrenheit(self,celsius):
        return celsius * 9/5 + 32

    def read_sensor(self):
        self.dht_sensor.measure()
        temperature_c = self.dht_sensor.temperature()
        self.temp = self.celsius_to_fahrenheit(temperature_c)
        self.hum = self.dht_sensor.humidity()
        #min temp
        if self.temp_min is None or self.temp < self.temp_min:
            self.temp_min = self.temp
        #max temp
        if self.temp_max is None or self.temp > self.temp_max:
            self.temp_max = self.temp
        #min hum
        if self.hum_min is None or self.hum < self.hum_min:
            self.hum_min = self.hum
        #max hum
        if self.hum_max is None or self.hum > self.hum_max:
            self.hum_max = self.hum
    # get the json
    def get_json(self,mac_address):
        data = {
            'mac_address' : mac_address,
            'gpio' : self.gpio,
            'temp' : self.temp,
            'temp_min' : self.temp_min,
            'temp_max' : self.temp_max,
            'hum' : self.hum,
            'hum_min' : self.hum_min,
            'hum_max' : self.hum_max
        }
        return data
    # resets the min and max values
    def reset_min_max(self):
        self.temp_min = None
        self.temp_max = None
        self.hum_max = None
        self.hum_min = None
