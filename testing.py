import network
import urequests
import ujson
import uio
import ubinascii
from sensors import sensors
from api import WebServer
import wifi_info
# Function to connect to WiFi
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print("Connected to WiFi!")
    ip = wlan.ifconfig()[0]
    print("IP Address:", ip)
    mac_address  = ubinascii.hexlify(wlan.config('mac'),':').decode()
    print("MAC Address:", mac_address)
    return ip, mac_address

# Function to load the JSON data from the API
def load_json_from_api(url):
    try:
        response = urequests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to load data from API.")
            return None
    except Exception as e:
        print("Error: ", e)
        return None

# Function to save JSON data to a local cache file
def save_json_to_cache(data, cache_filename):
    try:
        with open(cache_filename, "w") as f:
            ujson.dump(data, f)
        print("Data saved to cache.")
    except Exception as e:
        print("Error saving data to cache: ", e)

# Function to load JSON data from the local cache file
def load_json_from_cache(cache_filename):
    try:
        with open(cache_filename, "r") as f:
            return ujson.load(f)
    except Exception as e:
        print("Error loading data from cache: ", e)
        return None
ip, mac = connect_to_wifi(wifi_info.ssid,wifi_info.password)
api = WebServer(ip)

# Example usage
CACHE_FILE = "settings.json"

# Try loading data from the cache
cached_data = load_json_from_cache(CACHE_FILE)

if cached_data:
    print("Data loaded from cache:")
    #print(cached_data)
    hub_ip = cached_data['hub']['url']
    api.hub_ip = hub_ip
    SETTINGS_API_URL = f"http://{hub_ip}/plugins/NullSensors/api/pico/settings/{mac}"
    print(f"Data not found in cache, loading from API... {SETTINGS_API_URL}")
    data = load_json_from_api(SETTINGS_API_URL)
    if data:
        save_json_to_cache(data, CACHE_FILE)
        print("Data loaded from API and cached:")
        #print(data)
        #hub = data['hub']['url']
        if 'pico' in data:
            pico_json = data['pico']
            pico_sensors = sensors(pico_json,api)
            api.add_sensors(pico_sensors)
            pico_sensors.run()
else:
    print("Error: upload settings.json with hub url")