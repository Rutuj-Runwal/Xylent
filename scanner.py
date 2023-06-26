import hashlib
import os
import yara
from quarantineThreats import Quarantine

# rules_path = './rules/'
# rules_path = 'D:/Xylent/'

# peid_rules = yara.compile(filepaths={

#     'namespace1': rules_path+'eicar.yara'
# })
# peid_rules = yara.load(rules_path+"compiledRules")
# packer_rules = yara.compile(rules_path + 'packer.yar')
# crypto_rules = yara.compile(rules_path + 'crypto.yar')

#Path to the exe file you want to analyze
# exe_file_path = 'path/to/exe/file'

class Scanner:
    fileTypes = [".vbs", ".ps", ".ps1", ".rar", ".tmp", ".bas", ".bat", ".chm", ".cmd", ".com", ".cpl", ".crt", ".dll", ".exe", ".hta", ".js", ".lnk", ".msc", ".ocx", ".pcd", ".pif", ".pot", ".pdf", ".reg", ".scr", ".sct", ".sys", ".url", ".vb", ".vbe", ".wsc", ".wsf", ".wsh", ".ct", ".t", ".input",".war", ".jsp", ".jspx", ".php", ".asp", ".aspx", ".doc", ".docx", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx", ".tmp", ".log", ".dump", ".pwd", ".w", ".txt", ".conf", ".cfg", ".conf", ".config", ".psd1", ".psm1", ".ps1xml", ".clixml", ".psc1", ".pssc", ".pl", ".www", ".rdp", ".jar", ".docm", ".sys"]

    def __init__(self,signatures,rootPath):
        self.__signatures = signatures
        # self.__rootPath = rootPath
        self.__rootPath = "./"
        print(rootPath)
        self.peid_rules = yara.load(self.__rootPath+"\compiledRules")
        print("-----Scanner Initialized-----")
        self.quar = Quarantine()

    def getFileHash(self,path):
        hash = ""
        try:
            with open(path,'rb') as f:
                bytes = f.read()
                hash = hashlib.sha256(bytes).hexdigest()
                f.close()
            if hash!="":
                return hash
        except (PermissionError, OSError):
            # TODO: Run app with admin privilage to avoid PermissionError or OSError for certain locations and filetypes
            # print("Permission Error")
            return "RR_permission_error"

    def scanFile(self,path):
            print(path)
            detectionSpace = '' 
            suspScore = 0
            hashToChk = self.getFileHash(path)
            # Time Taken: O(n) 
            # TODO: optimize using Binary search for O(log(n))
            # Signature based detection
            if hashToChk == "RR_permission_error":
                return "SKIPPED"
        
            elif hashToChk!="":
                for hash in self.__signatures:
                    if hash==str(hashToChk):
                        print(self.__signatures[hash])
                        from plyer import notification
                        notif_str = "Xylent taking action against detected malware "+ path
                        suspScore+=100
                        detectionSpace = "SignatureBased: " + self.__signatures[hash]
            # YARA RULES DETECTION
            try:
                matches = self.peid_rules.match(path)
                if matches:
                    suspScore+=40
                    print(matches)
                    from plyer import notification
                    notif_str = "Xylent is taking action against detected malware "+ path
                    detectionSpace += " Yara: "+"YaraBasedEntity"
                    # return "aeicar!"
            except Exception:
                print('packer exception')

            if suspScore >= 40:
                notification.notify(
                    title="Malware Detected",
                    message=notif_str,
                    # displaying time
                    timeout=2
                )
                self.quar.quarantine(path)

            return detectionSpace
            # TODO: if file is packed: additional detection
            # TODO: if file is a .zip,.rar,.7z and other varients ADDITIONAL detections

    
    def scanFolders(self,location):
        directories = []
        if isinstance(location, list):
            for target in location:
                for (dirpath, dirnames, filenames) in os.walk(target):
                    directories += [os.path.join(dirpath, file) for file in filenames]
        elif isinstance(location, str):
            for (dirpath, dirnames, filenames) in os.walk(location):
                directories += [os.path.join(dirpath, file) for file in filenames]

        # Scan the files 
        # TODO: investigate for better performance with binary search and other methods?
        # TODO: develop a caching heuristic to scan files only after a certain age has passed
        scanReport = {}
        for files in directories:
            # print(files)
            try:
                # TODO: use os.path.splittext or other effective alternatives
                fileExtension = "."+files.split(".")[-1]
            except Exception:
                # TODO: better way to get file-extension. Prevent filename "cloaking" malware i.e. foo.txt.exe
                fileExtension = ".unknown"
                print("Internal temporary Skipped: "+files)
            if fileExtension in self.fileTypes:
                verdict = self.scanFile(files)
                if verdict != None and verdict != "" and verdict != "SKIPPED":
                    print(verdict+" detected!"+" for "+files)
                    scanReport[files] = verdict
                elif verdict == None:
                    print("Clean File " + files)
                    scanReport[files] = "CLEAN"
                elif verdict == "SKIPPED":
                    scanReport[files] = "SKIPPED"
                else:
                    print("Verdict: SAFE"+verdict+" for "+files)
                    scanReport[files] = "SAFE"
        return scanReport
