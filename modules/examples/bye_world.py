from termcolor import colored, cprint
from module import Module

import threading
import time

class CustomModule(Module):
    def __init__(self):
        information = {"Name": "My bye module",
                       "Description": "Test module",
                       "Author": "pepe"}

        # -----------name-----default_value--description--required?
        options = {"message": ["bye world!", "Message for you", True],
                   "option2": [None, "Text description", False],
                   "option3": [None, "Text description", False]}

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self._option_name = None


        

    # This module must be always implemented, it is called by the run option
    def run_module(self):

        def go():
            print(self.args["message"])

            t = threading.currentThread()
            while getattr(t, "do_run", True):
                print("soy un job")
                time.sleep(10)

        thread1 = threading.Thread(target=go)
        thread1.start()        
       
        super(CustomModule, self).run(t=thread1)
