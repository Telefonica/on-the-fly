import paho.mqtt.client as mqtt
from termcolor import colored, cprint
from module import Module

import threading
import time

from printib import print_error, print_info, print_ok
from scapy.all import *

class CustomModule(Module):
    def __init__(self):
        information = {"Name": "MQTT publish",
                       "Description": "Launch this module publish data through MQTT (Mosquitto)",
                       "Author": "@josueencinar y Marcos Rivea (@marcos_rm_98)"}

        # -----------name-----default_value--description--required?
        # -----------name-----default_value--description--required?
        options = {
            "rhost": ["broker.emqx.io", "rhost", True],
            "port": ["1883", "port", True],
            "sensor": ["/python/mqtt", "Sensor to change data", True],
            "data": ["{'motion':'1'}", "Data to be sent", True],
            "clienid": ["MQTTClient", "Client ID", True],
        }

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self._option_name = None
        self.client = None

    
    # This module must be always implemented, it is called by the run option
    def run_module(self):
        rhost = self.options.get("rhost")[0]
        port = int(self.options.get("port")[0])
        sensor = self.options.get("sensor")[0]
        data = self.options.get("data")[0]
        clienid = self.options.get("clienid")[0]

        print_ok("Connecting...")
        self.client = mqtt.Client(client_id = clienid)
        self.client.on_connect = CustomModule.__on_connect
        try:
            self.client.connect(rhost, port, 60)
            print_ok("Sending packet...")
            self.client.publish(sensor, data)
            print_ok("Packet sent")
        except Exception as e:
            print_error(e)

    @staticmethod
    def __on_connect(client, userdata, flags, rc):
        print_ok("Connection successful!")