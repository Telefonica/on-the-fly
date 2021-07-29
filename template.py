from termcolor import colored, cprint
from module import Module

class CustomModule(Module):
    def __init__(self):
        information = {"Name": "My own test",
                       "Description": "Large description",
                       "Author": "xxx"}



        # -----------name-----default_value--description--required?
        options = {"message": ["hello world!", "Message for you", True],
                   "option2": [None, "Text description", False],
                   "option3": [None, "Text description", False]}

        # Constructor of the parent class
        super(CustomModule, self).__init__(information, options)

        # Class atributes, initialization in the run_module method
        # after the user has set the values
        self._option_name = None

    # This module must be always implemented, it is called by the run option
    def run_module(self):
        print(self.args["message"])

        #super(CustomModule, self).run(function="hh")