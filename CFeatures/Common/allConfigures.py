import simplejson
import os


class Allconfiguration:
    pardir = os.path.dirname(__file__)
    with open(os.path.join(pardir, "config.json"), "r") as conf:
        configures: str = conf.read()
        configures_json:dict = simplejson.loads(configures)

    def getConfiguresJson(self):
        return self.configures_json



if __name__ == '__main__':
    print(__file__)
    print(os.path.dirname(__file__))
    print(Allconfiguration.configures_json['api_key'])
