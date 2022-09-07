import yaml
from service_core.config.config_object import Obj

class ConfigurationLoader:
    @staticmethod
    def load(path):
        with open(path) as file:
            documents = yaml.full_load(file)
        doc = Obj(documents)
        return doc

