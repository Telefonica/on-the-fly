from termcolor import colored, cprint
from module import Module
from xml.etree import cElementTree as ET
import socket
import select
import zeroconf
from datetime import datetime, timedelta
import re
import requests

class CustomModule(Module):
    def __init__(self):
        information = {"Name": "ssdp_scan",
                       "Description": "Using this module you will be able to discover active devices through SSDP protocol,\nThis module is a port of the HomePwn module made by @josueencinar and @pablogonzalezpe",
                       "Author": "@josueencinar"}

        # -----------name-----default_value--description--required?
        options = {"timeout": ["5", "Default timeout", True],
                   "service": ["ssdp:all", "Service type string to search for", False]}

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self.SSDP_MX = 2
        self.SSDP_TARGET = ("239.255.255.250", 1900)

    # This module must be always implemented, it is called by the run option
    def run_module(self):

        def _ssdp_request(self, ssdp_st):
            """Return request bytes for given st and mx."""
            return "\r\n".join([
                'M-SEARCH * HTTP/1.1',
                'ST: {}'.format(ssdp_st),
                'MX: {:d}'.format(self.SSDP_MX),
                'MAN: "ssdp:discover"',
                'HOST: {}:{}'.format(*self.SSDP_TARGET),
                '', '']).encode('utf-8')

        def _get_sockets(self):
            sockets = []
            for addr in zeroconf.get_all_addresses():
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    # Set the time-to-live for messages for local network
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL,
                                    self.SSDP_MX)
                    sock.bind((addr, 0))
                    sockets.append(sock)
                except socket.error:
                    pass
            return sockets

        def _parse_result(self, devices):
            # avoid duplicates
            my_list = []
            if not devices:
                print("| No devices found |")
            else:
                for device in devices:
                    try:
                        ip = device.replace("http://","").split(":")[0]
                        if ip not in my_list:
                            my_list.append(ip)
                            response = requests.get(device)
                            if response.status_code == 200:
                                _info_extract(self, response.text, ip)
                                print("")
                    except:
                        pass

        def _show_result(self, result):
            for k, v in result.items():
                cprint(k, "yellow")
                cprint(f"|_ {v}")

        def _info_extract(self, data, ip):
            search = ["friendlyName", "manufacturer"]
            result = {"ip": ip}
            tree = ET.fromstring(data)

            for t in tree.getiterator():
                tag = t.tag.split("}")[1]
                if tag in search:
                    result[tag] = t.text
            _show_result(self, result)

        """Send a message over the network to discover uPnP devices.
        Inspired in https://github.com/home-assistant/netdisco/blob/master/netdisco/ssdp.py
        """
        devices = []
        timeout = int(self.options["timeout"][0])
        ssdp_requests = _ssdp_request(self, self.options["service"][0])
        stop_wait = datetime.now() + timedelta(seconds=timeout)
        sockets = _get_sockets(self)

        for sock in [s for s in sockets]:
            try:
                sock.sendto(ssdp_requests, self.SSDP_TARGET)
                sock.setblocking(False)
            except socket.error:
                sockets.remove(sock)
                sock.close()
        try:
            while sockets:
                time_diff = stop_wait - datetime.now()
                seconds_left = time_diff.total_seconds()
                if seconds_left <= 0:
                    break

                ready = select.select(sockets, [], [], seconds_left)[0]

                for sock in ready:
                    try:
                        data, address = sock.recvfrom(1024)
                        response = data.decode("utf-8")
                        data = re.findall("LOCATION: .*", response)
                        for line in data:
                            devices.append(line.split(": ")[1].strip())
                    except UnicodeDecodeError:
                        cprint(f"| Ignoring invalid unicode response from {address} |", "magenta")
                        continue
                    except socket.error:
                        cprint("| Socket error while discovering SSDP devices |", "magenta")
                        sockets.remove(sock)
                        sock.close()
                        continue
        finally:
            for s in sockets:
                s.close()

        _parse_result(self, devices)