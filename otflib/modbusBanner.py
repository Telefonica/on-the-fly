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

import socket  
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.mei_message import *
from pymodbus.diag_message import *
#https://github.com/riptideio/pymodbus
#https://github.com/riptideio/pymodbus/blob/master/LICENSE
from printib import * 

def modbusBanner(rhost,port):  
    
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((rhost, int(port)))
        dataBytes = ("\x44\x62\x00\x00\x00\x05\x00\x2b\x0e\x03\x00").encode()
        client.send(dataBytes)
        response = client.recv(2048)
        #Parse common response
        responseList = str(response).split('\\')
        vendorName = responseList[12]
        vendorName = vendorName[1 :]
        productCode = responseList[14]
        productCode = productCode[3 :]
        majorMinorRevision = responseList[16]
        majorMinorRevision = majorMinorRevision [3 :]
        vendorUrl = responseList[18]
        vendorUrl =vendorUrl [3 :]
        productName = responseList[20]
        productName =productName [3 :]
        modelName = responseList[22]
        modelName =modelName [3 :-1]
        #Print common response
        print_info("Common banner:")
        print_info("Vendor:\t%s" % vendorName)
        print_info("productCode:\t%s" % productCode)
        print_info("majorMinorRevision:\t%s" % majorMinorRevision)
        print_info("vendorUrl:\t%s" % vendorUrl)
        print_info("productName:\t%s" %productName)
        print_info("modelName:\t%s" %modelName)
        print()

    except Exception as exc:
        print_info("Uncommon banner:")
        try:
            client2 = ModbusClient(rhost, port)
            client2.connect()
            rq = ReadDeviceInformationRequest(unit=0x1,read_code=0x03)
            rr = client2.execute(rq)
            print_info(rr.information)

        except Exception as e:
            print_error("Exception: "+str(e))

    client.close()
