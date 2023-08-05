# NullPicoSensors

 [MicroPython](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html) for running sensors on a pico and reporting back to NullSensors

## setup

add settings.json

```json
{
    "motion":[
        {
            "gpio": 1
        }
    ],
    "temperature":[
        {
            "gpio": 2
        }
    ],
    "buttons":[
        {
            "gpio": 13
        }
    ],
    "light":[
        {
            "gpio": 27
        }
    ]
}
```

add wifi_info.py

```python
ssid = 'your_wifi_network_ssid'
password = 'your_wifi_network_password'
```
