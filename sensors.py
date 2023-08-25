import time
import json
import machine
from picozero import pico_led
from temperature import temperature
from light import light
from motion import motion
from button import button
#
# handles running the sensors and reporting back to the null hub
#
class sensors:
    #
    # setup the sensors per the pico settings
    #
    def __init__(self,pico,api):
        print("creating sensors class object thing?")
        print(pico)
        self.api = api
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
        self.show_index = -1
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
            self.add_buttons(pico['buttons'])
        elif "buttons" in data:
            self.add_buttons(data['buttons'])
        # add pico button
        if "pico_button" in pico:
            print("add pico button")
            self.pico_button = button(pico['pico_button']['gpio'])
        elif "pico_button" in data:
            print("add pico button")
            self.pico_button = button(data['pico_button']['gpio'])
    #
    # add the temperature sensors
    #
    def add_temperature_sensors(self,_sensors):
        for sensor in _sensors:
            self.temperature_sensors.append(temperature(sensor['gpio'],sensor['remote_id'],sensor['name'],self.mac_address))
    #
    # add the motion sensors
    #
    def add_motion_sensors(self,_sensors):
        for sensor in _sensors:
            print(sensor)
            self.motion_sensors.append(motion(sensor['gpio'],sensor['remote_id'],sensor['name'],self.mac_address))
    #
    # add the light sensors
    #
    def add_light_sensors(self,_sensors):
        for sensor in _sensors:
            self.light_sensors.append(light(sensor['gpio'],sensor['remote_id'],sensor['name'],self.mac_address))
    #
    # add the buttons
    #
    def add_buttons(self,_sensors):
        for sensor in _sensors:
            self.buttons.append(button(sensor['gpio']))
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
    # get json data object
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
            data['temperature'].append(sensor.get_json())
        for sensor in self.light_sensors:
            data['light'].append(sensor.get_json())
        for sensor in self.motion_sensors:
            data['motion'].append(sensor.get_json())
        return data
    #
    # api info
    #
    def info(self):
        data = {
            "info": {
                "mac_address":self.mac_address,
                "name":self.name,
                "url":self.url,
                "type":"pico",
                "hub": self.api.hub_ip,
                "enabled": True,
                "main": 0,
                "dev": "production",
                "git":"https://github.com/sophiathekitty/NullPicoSensors"
            }
        }
        return json.dumps(data)
    #
    # api temperature sensors
    #
    def temperature(self):
        data = {"temperature":[]}
        for sensor in self.temperature_sensors:
            data["temperature"].append(sensor.get_json())
        return json.dumps(data)
    #
    # api light sensors
    #
    def light(self):
        data = {"light":[]}
        for sensor in self.light_sensors:
            data['light'].append(sensor.get_json())
        return json.dumps(data)
    #
    # api motion sensors
    #
    def motion(self):
        data = {"motion":[]}
        for sensor in self.motion_sensors:
            data['motion'].append(sensor.get_json())
        return json.dumps(data)
    #
    # send the report
    #
    def send_report(self):
        data = self.get_pico_json()
        for sensor in data['temperature']:
            print(f"{sensor['name']}:")
            print(f"Temp: {sensor['temp']} - {sensor['temp_max']} / {sensor['temp_min']}")
            print(f"Hum: {sensor['hum']} - {sensor['hum_max']} / {sensor['hum_min']}")
        for sensor in data['light']:
            print(f"Light({sensor['name']}): {sensor['level']} - {sensor['max']} / {sensor['min']}")
        for sensor in data['motion']:
            print(f"Motion({sensor['name']}): {sensor['level']}")
        self.last_report = time.time()
        self.reset_min_max_levels()
    #
    # reset the min max levels
    #
    def reset_min_max_levels(self, force=False):
        if(self.is_time_to_reset_min_max() or force):
            for sensor in self.temperature_sensors:
                sensor.reset_min_max()
            if(force):
                for sensor in self.light_sensors:
                    sensor.reset_min_max()
        for sensor in self.motion_sensors:
            sensor.reset_min_max()
    #
    # do pico led blink countdown
    #
    def blink_led_countdown(self,count):
        for i in range(count,0,-1):
            print(i)
            self.blink_led(i)
            time.sleep_ms((300*(count-i))+500)
    #
    # blink pico led
    #
    def blink_led(self,count):
        for i in range(0,count):
            pico_led.on()
            time.sleep_ms(100)
            pico_led.off()
            time.sleep_ms(200)
    #
    # slow blink pico led
    #
    def slow_blink_led(self,count):
        for i in range(0,count):
            pico_led.on()
            time.sleep_ms(500)
            pico_led.off()
            time.sleep_ms(500)
    #
    # set motion sensors to show motion
    #
    def show_motion(self):
        self.show_index += 1
        if self.show_index >= len(self.motion_sensors):
            self.show_index = -1
        if self.show_index >= 0:
            self.blink_led(self.show_index+1)
        for i in range(0,len(self.motion_sensors)):
            if i == self.show_index:
                self.motion_sensors[i].show = True
            else:
                self.motion_sensors[i].show = False
    #
    # run pico button
    #
    def run_pico_button(self):
        if self.pico_button.report_clicked():
            print("pico button clicked - show motion")
            self.slow_blink_led(1)
            self.show_motion()
        elif self.pico_button.report_double_clicked():
            print("pico button double clicked - reset min max")
            self.slow_blink_led(2)
            self.reset_min_max_levels(True)
        elif self.pico_button.report_down(5000):
            print("pico button long press. rebooting...")
            # blink led count
            self.blink_led_countdown(5)
            # reboot the pico
            machine.reset()
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
                # do the report
                if self.is_time_to_do_report():
                    print("report sensors and reset the min max stuff")
                    self.send_report()
                # check the buttons
                for button in self.buttons:
                    button.state()
                    if button.report_pressed():
                        print("button pressed")
                    if button.report_clicked():
                        print("button clicked")
                self.pico_button.state()
                # check the pico button exists and run it
                if 'pico_button' in self.__dict__:
                    self.run_pico_button()
                # run the api
                self.api.run()
            except OSError as e:
                print("Error:", e)
            # Wait for 0.005 seconds before taking the next reading
            time.sleep_ms(5)
