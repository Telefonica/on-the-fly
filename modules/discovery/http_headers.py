from termcolor import colored, cprint
from module import Module

import threading
import time

import requests

from printib import print_error, print_info, print_ok
import json

class CustomModule(Module):
    def __init__(self):
        information = {"Name": "HTTP Headers",
                       "Description": "Gets HTTP headers of a website",
                       "Author": "Marcos Rivera Martínez"}

        # -----------name-----default_value--description--required?
        options = {"url": [None, "The url of the website", True]}

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self._option_name = None

    
    # This module must be always implemented, it is called by the run option
    def run_module(self):

        error = False
        web = self.options.get("url")[0]

        try:
            print_ok("Getting HTTP Headers...")
            response = requests.get(web) 
            print_ok("Status code of the website {}".format(response.status_code))
        except:
            error = True
            print_error("The url is not right")

        if not error:
            headers_json = json.dumps(
                    dict(response.headers),
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': ')
            )
            print_info(headers_json)   