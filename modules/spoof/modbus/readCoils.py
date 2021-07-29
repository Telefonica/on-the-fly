from termcolor import colored, cprint
from module import Module
from scapy.all import *
import threading
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
#https://github.com/riptideio/pymodbus
#https://github.com/riptideio/pymodbus/blob/master/LICENSE

import time
from printib import * 
import logging




class CustomModule(Module):
    def __init__(self):
        information = {"Name": "Modbus Read Coils",
                       "Description": "Read Coils at the specific register",
                       "Author": "Luis Eduardo Álvarez @luisedev"}

        # -----------name-----default_value--description--required?
        options = { "rport":        [502, "Target Port", True],
                    "rhost":        ["", "Servers IP", True],
                    "register":     ["1","Register address value",True],
                    "count":         ["1","Number of coils to read", True],
                    "unit":         ["1","Slave UNIT",True],
                    "verbose":      ["False","Verbose mode", False]
                    }

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self._option_name = None

    
    # This module must be always implemented, it is called by the run option
    def run_module(self):
        FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
        logging.basicConfig(format=FORMAT)

        if(self.options["verbose"][0]=="True"):
            log = logging.getLogger()
            log.setLevel(logging.DEBUG)
        else:
            
            log = logging.getLogger()
            log.setLevel(logging.ERROR)
            
        try:
            client = ModbusClient(self.options["rhost"][0], port=str(self.options["rport"][0]))
            client.connect()
            rr = client.read_coils(int(self.options["register"][0]), int(self.options["count"][0]), unit=int(self.options["unit"][0]))
            
            print_info(rr.bits)
            assert(rr.bits[0] == True)
            if(self.options["verbose"][0]=="True"):
                log.debug(rr)
            
                    
        except Exception as e:
            print_error(str(e))
