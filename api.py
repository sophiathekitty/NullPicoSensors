# non blocking web server class to run a simple web api in line with the sensors classes
import socket
import time
import select

class WebServer:
    def __init__(self, ip, port=80,hub_ip=None):
        print(f"Starting web server... {ip}:{port}")
        self.ip = ip
        self.port = port
        self.hub_ip = hub_ip
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen(5)
        self.server_socket.setblocking(False)
        self.inputs = [self.server_socket]
        self.url_handlers = {}
        self.url_handlers['/'] = self.handle_root
        self.url_handlers['/api/info'] = self.handle_info
        self.url_handlers['/plugins/NullSensors/api/motion'] = self.handle_motion_sensors
        self.url_handlers['/plugins/NullSensors/api/temperature'] = self.handle_temperature_sensors
        self.url_handlers['/plugins/NullSensors/api/light'] = self.handle_light_sensors
        self.url_handlers['/api/motion'] = self.handle_motion_sensors
        self.url_handlers['/api/temperature'] = self.handle_temperature_sensors
        self.url_handlers['/api/light'] = self.handle_light_sensors
        self.url_handlers['/api/info/'] = self.handle_info
        self.url_handlers['/plugins/NullSensors/api/motion/'] = self.handle_motion_sensors
        self.url_handlers['/plugins/NullSensors/api/temperature/'] = self.handle_temperature_sensors
        self.url_handlers['/plugins/NullSensors/api/light/'] = self.handle_light_sensors
        self.url_handlers['/api/motion/'] = self.handle_motion_sensors
        self.url_handlers['/api/temperature/'] = self.handle_temperature_sensors
        self.url_handlers['/api/light/'] = self.handle_light_sensors

        self.sensors = None
    def add_sensors(self,sensors):
        self.sensors = sensors
    def handle_request(self, request):
        request_lines = request.split(b'\r\n')
        request_line = request_lines[0].decode()
        method, url, _ = request_line.split(' ')

        handler = self.url_handlers.get(url, None)
        if handler:
            return handler()
        else:
            return b"HTTP/1.1 404 Not Found\nContent-Type: text/html\n\n404 - Page not found"
    #
    # handlers
    #
    def error_response(self,status,message):
        return f"HTTP/1.1 {status} \nContent-Type: text/html\n\n{message}"
    def html_response(self,status,message):
        return f"HTTP/1.1 {status} \nContent-Type: text/html\n\n{message}"
    def json_response(self,status,message):
        return f"HTTP/1.1 {status} \nContent-Type: application/json\n\n{message}"
    def handle_root(self):
        return self.html_response(200,"<doctype html><html><head><title>NullPicoSensors</title></head><body style='background-color:#2f4f4f;color:#cad7e4;'><h1 style='color:#98ed8a;'>Null Pico Sensors</h1><p>Null Pico Sensors is running.</p><ul><li><a color='##d3d3d3' href='/api/info'>info</a></li><li><a color='##d3d3d3' href='/api/temperature'>temp</a></li><li><a color='##d3d3d3' href='/api/light'>light</a></li><li><a href='/api/motion'>motion</a></li></ul></body></html>")
    def handle_info(self):
        if self.sensors:
            return self.json_response(200,self.sensors.info())
        return self.error_response(500,"Sensors not configured for web server")
    def handle_motion_sensors(self):
        if self.sensors:
            return self.json_response(200,self.sensors.motion())
        return self.error_response(500,"Sensors not configured for web server")
    def handle_temperature_sensors(self):
        if self.sensors:
            return self.json_response(200,self.sensors.temperature())
        return self.error_response(500,"Sensors not configured for web server")
    def handle_light_sensors(self):
        if self.sensors:
            return self.json_response(200,self.sensors.light())
        return self.error_response(500,"Sensors not configured for web server")
    #
    # call as part of main loop
    #
    def run(self):
        readable, _, _ = select.select(self.inputs, [], [], 0)
        for s in readable:
            if s is self.server_socket:
                client_socket, address = self.server_socket.accept()
                print(f"Connection from {address}")
                client_socket.setblocking(False)
                self.inputs.append(client_socket)
            else:
                try:
                    data = s.recv(1024)
                    if data:
                        #print("Received:", data)
                        response = self.handle_request(data)
                        s.sendall(response)
                        # Optionally, you can close the connection after sending the response
                        s.close()
                        self.inputs.remove(s)
                    else:
                        print("Closing connection")
                        s.close()
                        self.inputs.remove(s)
                except Exception as e:
                    print("Error: ", e)
                    s.close()
                    self.inputs.remove(s)