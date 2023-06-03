import os
import shutil

class Quarantine:
    def __init__(self,file):
        self.file = file
        self.fileName = file.split("\\")[-1]
        print("Name of file:"+self.fileName)
        print("Path of file:"+self.file)
        
    def killProcess(self):
        # Try to kill the process if it's active in system's memory
        try:
            os.system("taskkill /f /im "+self.fileName)
        except Exception:
            print("Cant kill, threat not active / Not an executable type")
            # print(self.file)
    
    def quarantine(self):
        try:
            # Kill the process

            # TODO: Kill only if filetype's category is executable
            self.killProcess()

        finally:
            # Qurantine the threat

            # Check if quarantine directory exists
            # QuarantinePath = "C:\ProgramData\Xylent_Quars"
            QuarantinePath = R"%UserProfile%/Documents/Xylent_Quars"
            QuarantineDir = os.path.expandvars(QuarantinePath)

            if not os.path.exists(QuarantineDir):
                try:
                    os.mkdir(QuarantineDir)
                except FileNotFoundError:
                    print("Cannot create quarantine folder")
                    # TODO: Create a universal backup quarantine path

            # TODO: Add encryption-decryption mechanic to the quarantine process
            fileToMove = os.path.join(QuarantineDir, self.fileName)
            
            # TODO: fix PermissionError by getting admin elevated access
            # os.replace(self.file, fileToMove)
            shutil.move(self.file,fileToMove)
            
