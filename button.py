import machine

class button():
    # Connect the motion sensor to GPIO pin ie: 13 for GP13
    def __init__(self,pin):
        print(f"add light sensor on pin: {pin}")
        self.gpio = pin
        # Connect the button to GPIO 17 (Pin GP13)
        self.push_button = machine.Pin(pin, machine.Pin.IN)
        self.button_down = False
        self.button_state = "up"
    # returns true when button released
    def state(self):
        pressed = self.push_button.value() == 1
        if pressed and not self.button_down:
            self.button_down = True
            self.button_state = "pressed"
        elif not pressed and self.button_down:
            self.button_down = False
            self.button_state = "clicked"
        elif self.button_down:
            self.button_state = "down"
        else:
            self.button_state = "up"
        return self.button_state
    # report pressed
    def report_pressed(self):
        return self.state() == "pressed"
    # report pressed
    def report_clicked(self):
        return self.state() == "clicked"
