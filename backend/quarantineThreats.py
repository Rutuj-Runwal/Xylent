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
                # TODO: Create a universal backup/"fallback" quarantine path - (probably in current root?)

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
            # os.replace(self.file, fileToMove)
            self.store.setVal(str(file),detectionSpace)
            shutil.move(str(file),str(fileToMove))   
            print("DONE IN QUARS!!!")   

    def quarantineFilesInArchive(self, originalZipPath, preserveArchiveContent):
        # originalZipPath = self.store.getVal('ZipPath')
        print("Original Zip Path: "+str(originalZipPath))
        fileName = originalZipPath.split("\\")[-1]
        # print("Name of file:"+str(fileName))
        tempZipPath = "./scanExtracts"
        if not os.path.exists(tempZipPath):
            os.mkdir(tempZipPath)
        if preserveArchiveContent:
            # STABLE BUT SLOW - COPIES/REPLACES FILES
            '''In order to preserve files in archive, only malicious file(s) from the archive is removed'''
            # Other contents deemed safe are re-zipped at a temp location where the file was unzipped
            # Finally, we replace the file at that location
            shutil.make_archive(fileName.split(".")[0], fileName.split(".")[
                                1], root_dir=tempZipPath)
            # Replace the repaired archive in the original path
            # filename without the extension of file is needed
            # fileextension assumed to be format
            shutil.move("./"+fileName, str(originalZipPath))
            shutil.rmtree(tempZipPath)
            print("Preserved!")
        else:
            '''Do not preserve and quarantine the entire zip file'''
            self.quarantine(originalZipPath, "HARMFUL ZIP FILE")
            print("Not Preserved!")

    def restore(self,originalPath):
        fileName = originalPath.split("\\")[-1]
        quarPath = os.path.join(self.QuarantineDir,fileName)
        self.store.removeVal(originalPath)
        if os.path.exists(quarPath):
            shutil.move(quarPath,originalPath)
        else:
            print("File Not Found, removing quarantine record!")
    
    def remove(self,originalPath):
        fileName = originalPath.split("\\")[-1]
        quarPath = os.path.join(self.QuarantineDir, fileName)
        self.store.removeVal(originalPath)
        if os.path.exists(quarPath):
            os.remove(quarPath)
        else:
            print("File Not Found, removing quarantine record!")
