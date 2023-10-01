import os
import json
class ParseJson:
    def __init__(self,configFilePath,configFileName,defaults):
        if not os.path.exists(configFilePath):
            os.mkdir(configFilePath)
        self.PATH = os.path.join(configFilePath, configFileName+'.json')
        self.defaults = defaults
        self.data = self.parseDataFile(defaults)
    
    def keyExists(self,key):
        data = self.parseDataFile(self.defaults)
        if key in data:
            return True
        else:
            return False

    def getVal(self,key):
        return self.data[key]
    
    def setVal(self,key,val):
        self.data = self.parseDataFile(self.defaults)
        self.data[key] = val
        with open(self.PATH, 'w') as file_obj:
            json.dump(self.data, file_obj)
            #file_obj.close()

    def removeVal(self,key):
        with open(self.PATH,'r') as fp:
                parsed_data = json.load(fp)
                #fp.close()
        del parsed_data[key]
        with open(self.PATH, 'w') as fp:
            json.dump(parsed_data, fp)
            #fp.close()

    def purge(self):
        with open(self.PATH, 'w') as fp:
            json.dump({}, fp)

    def parseDataFile(self,defaults):
        try:
            with open(self.PATH,'r') as fp:
                parsed_data = json.load(fp)
                #fp.close()
            return parsed_data
        except Exception as e:
            # print(e)
            with open(self.PATH, 'w') as fp:
                json.dump(defaults, fp)
                #fp.close()
            return defaults
