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
        self.down_count = 0
        self.click_count = 0
        self.click_countdown = 0
    # returns true when button released
    def state(self):
        pressed = self.push_button.value() == 1
        if pressed and not self.button_down:
            self.button_down = True
            self.button_state = "pressed"
        elif not pressed and self.button_down and self.down_count < 500:
            self.button_down = False
            self.click_count += 1
            if self.click_count == 1:
                self.button_state = "clicked"
            else:
                self.button_state = "double_clicked"
            self.click_countdown = 250
        elif self.button_down:
            self.button_state = "down"
            self.down_count += 1
        else:
            self.down_count = 0
            # count down the click (for double click)
            self.click_countdown -= 1
            if self.click_countdown < 0:
                self.button_state = "up"
                self.click_count = 0
        return self.button_state
    # report pressed
    def report_pressed(self):
        return self.state() == "pressed"
    # report pressed
    def report_clicked(self):
        return self.state() == "clicked" and self.click_countdown == 0
    # report double clicked
    def report_double_clicked(self):
        return self.state() == "double_clicked"
    # long press
    def report_down(self, length=500):
        return self.state() == "down" and self.down_count == length
