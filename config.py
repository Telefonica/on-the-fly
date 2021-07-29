import json

class Config:
    __instance = None
    __config = {}

    @staticmethod
    def get_instance():
        if Config.__instance == None:
            Config()
        return Config.__instance

    def __init__(self):
        if Config.__instance == None:
            Config.__instance = self
            self.__load_config()

    def __load_config(self):
        try:
            with open("config.json") as config:
                self.__config = json.load(config)
        except:
            pass
        
        # Path must to end in /
        
    
    def get_config(self):
        return self.__config
    