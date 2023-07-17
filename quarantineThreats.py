import os
import shutil
from parseJson import ParseJson
class Quarantine:        

    def __init__(self,data=None):
        # print(data)
        if data:
            self.store = ParseJson(data["configFilePath"], data["configFileName"], data["defaults"])
        # Check if quarantine directory exists
        # QuarantinePath = "C:\ProgramData\Xylent_Quars"
        self.QuarantinePath = R"%UserProfile%\Documents\Xylent_Quars"
        self.QuarantineDir = os.path.expandvars(self.QuarantinePath)

        if not os.path.exists(self.QuarantineDir):
            try:
                os.mkdir(self.QuarantineDir)
            except FileNotFoundError:
                print("Cannot create quarantine folder")
                # TODO: Create a universal backup quarantine path

    def killProcess(self,fileName):
        # Try to kill the process if it's active in system's memory
        try:
            os.system("taskkill /f /im "+fileName)
        except Exception:
            print("Cant kill, threat not active / Not an executable type")
            # print(self.file)
    
    def quarantine(self, file,detectionSpace):
        fileName = file.split("\\")[-1]
        print("Name of file:"+fileName)
        print("Path of file:"+file)
        try:
            # Kill the process

            # TODO: Kill only if filetype's category is executable
            self.killProcess(fileName)

        finally:
            # Qurantine the threat

            # TODO: Add encryption-decryption mechanic to the quarantine process
            fileToMove = os.path.join(self.QuarantineDir, fileName)
            
            # TODO: fix PermissionError by getting admin elevated access
            # os.replace(self.file, fileToMove)
            self.store.setVal(str(file),detectionSpace)
            shutil.move(str(file),str(fileToMove))   
            print("DONE IN QUARS!!!")      

    def restore(self,originalPath):
        fileName = originalPath.split("\\")[-1]
        quarPath = os.path.join(self.QuarantineDir,fileName)
        self.store.removeVal(originalPath)
        shutil.move(quarPath,originalPath)
