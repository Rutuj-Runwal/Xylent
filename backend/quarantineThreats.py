import os
import shutil
import psutil
from parseJson import ParseJson

class Quarantine:
    def __init__(self, config_data=None):
        self.config = ParseJson(config_data["configFilePath"], config_data["configFileName"], config_data["defaults"])
        self.quarantine_path = os.path.expandvars(R"%UserProfile%\Documents\Xylent_Quars")
        self.quarantine_dir = os.path.join(self.quarantine_path)
        if not os.path.exists(self.quarantine_dir):
            try:
                os.mkdir(self.quarantine_dir)
            except FileNotFoundError:
                print("Cannot create quarantine folder")

    def kill_process(self, file_name):
        try:
            for process in psutil.process_iter(['pid', 'name']):
                try:
                    if file_name.lower() in process.info['name'].lower():
                        process.kill()
                        print(f"Process {process.info['name']} (PID: {process.info['pid']}) terminated.")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception:
            print("Can't kill, threat not active / Not an executable type")

    def quarantine(self, file_path, detection_space):
        file_name = os.path.basename(file_path)
        try:
            self.kill_process(file_name)
        finally:
            quarantine_file_path = os.path.join(self.quarantine_dir, file_name)
            self.config.setVal(str(file_path), detection_space)
            shutil.move(file_path, quarantine_file_path)
            print("DONE IN QUARS!!!")

    def quarantineFilesInArchive(self, originalZipPath, preserveArchiveContent):
        fileName = originalZipPath.split("\\")[-1]
        tempZipPath = "./scanExtracts"
        if not os.path.exists(tempZipPath):
            os.mkdir(tempZipPath)
        if preserveArchiveContent:
            shutil.make_archive(fileName.split(".")[0], fileName.split(".")[1], root_dir=tempZipPath)
            shutil.move("./" + fileName, str(originalZipPath))
            shutil.rmtree(tempZipPath)
            print("Preserved!")
        else:
            self.quarantine(originalZipPath, "HARMFUL ZIP FILE")
            print("Not Preserved!")

    def restore(self,originalPath):
        fileName = originalPath.split("\\")[-1]
        quarPath = os.path.join(self.quarantine_dir,fileName)
        self.config.removeVal(originalPath)
        if os.path.exists(quarPath):
            shutil.move(quarPath,originalPath)
        else:
            print("File Not Found, removing quarantine record!")
    
    def remove(self,originalPath):
        fileName = originalPath.split("\\")[-1]
        quarPath = os.path.join(self.quarantine_dir, fileName)
        self.config.removeVal(originalPath)
        if os.path.exists(quarPath):
            os.remove(quarPath)
        else:
            print("File Not Found, removing quarantine record!")
