from termcolor import colored, cprint
from module import Module

import threading
import time
import sys
from otflib.modbusBanner import modbusBanner


class CustomModule(Module):
    def __init__(self):
        information = {"Name": "Modbus Fingerprint",
                       "Description": "Gets modbus server info.",
                       "Author": "Luis Eduardo Álvarez @luisedev"}

        # -----------name-----default_value--description--required?
        options = {"rhost": [ "-", "Target IP", True],
                   "rport":  [502, "Target Port", True]}

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self._option_name = None

    
    # This module must be always implemented, it is called by the run option
    def run_module(self):

        rhost= self.options["rhost"][0]
        port = self.options["rport"][0]
        modbusBanner(rhost,port)
  
     