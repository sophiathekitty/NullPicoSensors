import time
import json
from temperature import temperature
from light import light
from motion import motion
#
# handles running the sensors and reporting back to the null hub
#
class sensors:
    #
    # setup the sensors per the pico settings
    #
    def __init__(self,pico):
        print("creating sensors class object thing?")
        print(pico)
        self.mac_address = pico['mac_address']
        self.name = pico['name']
        self.url = pico['url']
        self.temperature_sensors = []
        self.light_sensors = []
        self.motion_sensors = []
        self.buttons = []
        self.last_report = 0
        self.last_read =  0
        self.last_reset = time.time()
        # load the default sensor settings
        with open("sensors.json",'r') as file:
            print("loading sensors?")
            data = json.load(file)
            print(data)
        # add temperature sensors
        if "temperature" in pico:
            self.add_temperature_sensors(pico['temperature'])
        elif "temperature" in data:
            self.add_temperature_sensors(data['temperature'])
        # add light sensors
        if "light" in pico:
            self.add_light_sensors(pico['light'])
        elif "light" in data:
            self.add_light_sensors(data['light'])
        # add motion sensors
        if "motion" in pico:
            self.add_motion_sensors(pico['motion'])
        elif "motion" in data:
            self.add_motion_sensors(data['motion'])
        # add buttons
        if "buttons" in pico:
            self.add_motion_sensors(pico['buttons'])
        elif "buttons" in data:
            self.add_motion_sensors(data['buttons'])
    #
    # add the temperature sensors
    #
    def add_temperature_sensors(self,_sensors):
        for sensor in _sensors:
            self.temperature_sensors.append(temperature(sensor['gpio']))
    #
    # add the motion sensors
    #
    def add_motion_sensors(self,_sensors):
        for sensor in _sensors:
            self.motion_sensors.append(motion(sensor['gpio']))
    #
    # add the light sensors
    #
    def add_light_sensors(self,_sensors):
        for sensor in _sensors:
            self.light_sensors.append(light(sensor['gpio']))
    #
    # add the buttons
    #
    def add_buttons(self,_sensors):
        for sensor in _sensors:
            self.buttons.append(light(sensor['gpio']))
    #
    # has it been a minute
    #
    def is_time_to_do_report(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_report
        return elapsed_time >= 60
    #
    # has it been a minute
    #
    def is_time_to_reset_min_max(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_reset
        return elapsed_time >= (60*60)
    #
    # has it been a minute
    #
    def is_time_to_read_sensors(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_read
        return elapsed_time >= 2
    #
    # get json
    #
    def get_pico_json(self):
        data = {
            "mac_address":self.mac_address,
            "name":self.name,
            "url":self.url,
            "temperature":[],
            "light":[],
            "motion":[],
        }
        for sensor in self.temperature_sensors:
            data['temperature'].append(sensor.get_json(self.mac_address))
        for sensor in self.light_sensors:
            data['light'].append(sensor.get_json(self.mac_address))
        for sensor in self.motion_sensors:
            data['motion'].append(sensor.get_json(self.mac_address))
        return data
    #
    # send the report
    #
    def send_report(self):
        data = self.get_pico_json()
        print(f"Temp: {data['temperature'][0]['temp']} - {data['temperature'][0]['temp_max']} / {data['temperature'][0]['temp_min']}")
        print(f"Hum: {data['temperature'][0]['hum']} - {data['temperature'][0]['hum_max']} / {data['temperature'][0]['hum_min']}")
        print(f"Light: {data['light'][0]['level']} - {data['light'][0]['max']} / {data['light'][0]['min']}")
        print(f"Motion: {data['motion'][0]['level']}")
        self.last_report = time.time()
        self.reset_min_max_levels()
    #
    #
    #
    def reset_min_max_levels(self):
        if(self.is_time_to_reset_min_max()):
            for sensor in self.temperature_sensors:
                sensor.reset_min_max()
            for sensor in self.light_sensors:
                sensor.reset_min_max()
        for sensor in self.motion_sensors:
            sensor.reset_min_max()
    #
    #
    # run the sensors
    #
    #
    def run(self):
        print("running sensors")
        while True:
            try:
                # read the sensors wait 2 seconds between reading most sensors
                if self.is_time_to_read_sensors():
                    for sensor in self.temperature_sensors:
                        sensor.read_sensor()
                    for sensor in self.light_sensors:
                        sensor.read_sensor()
                    self.last_read = time.time()
                # do frequent motion sensor checks to minimize delay 
                for sensor in self.motion_sensors:
                    if sensor.read_sensor():
                        print("report new motion detected")
                if self.is_time_to_do_report():
                    # read the sensors
                    print("report sensors and reset the min max stuff")
                    self.send_report()
            except OSError as e:
                print("Error:", e)
            # Wait for 0.005 seconds before taking the next reading
            time.sleep_ms(5)
