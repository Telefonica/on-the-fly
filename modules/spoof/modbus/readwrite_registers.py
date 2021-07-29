'''
modbusBanner.py, readCoils.py, readDiscreteInputs.py, readHoldingRegisters.py, 
readInputRegisters.py, readwrite_registers.py, writeCoil.py, writeMultipleCoils.py, 
writeRegister.py use the pymodbus library which is licensed under the LICENSE
https://github.com/riptideio/pymodbus/blob/master/LICENSE

Copyright (c) 2011 Galen Collins
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. The name of the author may not be used to endorse or promote products
   derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

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
        information = {"Name": "Modbus Read Holding Registers",
                       "Description": "Read Holding Registers at the specific address",
                       "Author": "Luis Eduardo Álvarez @luisedev"}

        # -----------name-----default_value--description--required?
        options = { "rport":        ["502", "Target Port", True],
                    "rhost":        ["", "Servers IP", True],
                    "read_address":     ["1","Register address value",True],
                    "read_count":         ["1","Number of registers to read", True],
                    "write_address":         ["1","Register address value", True],
                    "write_value":         ["20","Write value", True],
                    "write_count":         ["2","Number of registers to write", True],
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

        read_address = int(self.options["read_address"][0])
        read_count = int(self.options["read_count"][0])

        write_address = int(self.options["write_address"][0])
        write_value = int(self.options["write_value"][0])
        write_count = int(self.options["write_count"][0])

        unit = int(self.options["unit"][0])
        

        try:
            client = ModbusClient(self.options["rhost"][0], port=str(self.options["rport"][0]))
            client.connect()

            arguments = {
                'read_address':   read_address,
                'read_count':      read_count,
                'write_address':   write_address,
                'write_registers': [write_value]*write_count,
            }

            log.debug("Read write registeres simulataneously")
            rq = client.readwrite_registers(unit=unit, **arguments)
            rr = client.read_holding_registers(1, 8, unit=unit)

            if(not rq.isError()):
                print_info("Written registers:"+ str(rq.registers))
                print_info("Read registers:"+ str(rr.registers))
       


        except Exception as e:
            print_error(str(e))
