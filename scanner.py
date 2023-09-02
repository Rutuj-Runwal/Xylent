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
    fileTypes = [".vbs", ".ps", ".ps1", ".rar", ".tmp", ".bas", ".bat", ".chm", ".cmd", ".com", ".cpl", ".crt", ".dll", ".exe", ".hta", ".js", ".lnk", ".msc", ".ocx", ".pcd", ".pif", ".pot", ".pdf", ".reg", ".scr", ".sct", ".sys", ".url", ".vb", ".vbe", ".wsc", ".wsf", ".wsh", ".ct", ".t", ".input", ".war",".jsp", ".jspx", ".php", ".asp", ".aspx", ".doc", ".docx", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx", ".tmp", ".log", ".dump", ".pwd", ".w", ".txt", ".conf", ".cfg", ".conf", ".config", ".psd1", ".psm1", ".ps1xml", ".clixml", ".psc1", ".pssc", ".pl", ".www", ".rdp", ".jar", ".docm", ".sys", ".zip", ".tar"]

    def __init__(self,signatures,rootPath):
        import sys
        self.__signatures = signatures
        if getattr(sys,'frozen',False):
            # Current Path
            self.__rootPath = "."
        else:
            self.__rootPath = rootPath
        self.quarantineData = {
            'configFileName':'quar_info',
            'configFilePath':self.__rootPath+'/config/',
            'defaults':{}
        }
        try:
            while not os.path.exists(self.__rootPath+"/compiledRules"):
                print("Waiting for resources to compile...")
            # Initialize yara rules
            self.peid_rules = yara.load(self.__rootPath+"/compiledRules")
        except Exception as e:
            print(e)
        print("-----Scanner Initialized-----")
        self.quar = Quarantine(self.quarantineData)

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
            print("Permission Error")
            return "RR_permission_error"
    
    def verifyExecutableSignature(self,path):
        import subprocess
        import time,datetime
        command = "(Get-AuthenticodeSignature" + " " + path + ").Status"
        process = subprocess.run(['Powershell', '-Command', command], stdout=subprocess.PIPE, encoding='utf-8')
        now = time.time()
        ageInSec = now-os.stat(path).st_mtime
        age = str(datetime.timedelta(seconds=ageInSec))
        # Valid - Trust
        # NotSigned - Low Suspicion - Score: 30
        # UnknownError - invalid # High Suspicion - Score: 50
        # HashMismatch - treat as invalid # High Suspicion - Score: 50
        # NotTrusted - Moderate Suspicion - Score: 40 
        if process.stdout.strip() == "HashMismatch" or process.stdout.strip() == "UnknownError":
            return {'score':50,'age':age}
        elif process.stdout.strip()=="NotTrusted":
            return {'score':40,'age':age}
        elif process.stdout.strip()=="NotSigned":
            return {'score':30,'age':age}
        else:
            return {'score':0,'age':age}
    
    def handleArchives(self, path):
        print("Handling Archive!!")
        import shutil
        try:
            archiveExtractPath = "./scanExtracts"
            print("----------------------------------------------------")
            print(archiveExtractPath.split("/")[1])
            print(path)
            print("----------------------------------------------------")
            if archiveExtractPath.split("/")[1] in path:
                print("Skipped to avoid recursion.Depth=1 for scanning archives!")
                return "Done!"
            else:
                if not os.path.exists(archiveExtractPath):
                    os.mkdir(archiveExtractPath)
                shutil.unpack_archive(path, archiveExtractPath)
                verdicts = self.scanFolders(archiveExtractPath)
                # dictionary in scanFolders leads to O(1) time
                if "SignatureBased" or "Yara" in verdicts:
                    if os.path.exists(archiveExtractPath):
                        print("Malware detected in archive")
                        # from plyer import notification
                        # notification.notify(
                        #     title="Archive Repaired",
                        #         message="Archive with malicious content repaired.Malware removed,Safe content Preserved!",
                        #         # displaying time
                        #         timeout=1
                        # )
                        from notifypy import Notify
                        notification = Notify()
                        notification.title = "Archive Repaired"
                        notification.message = "Archive with malicious content repaired.Malware removed,Safe content Preserved!"
                        notification.send()
                        self.quar.quarantineFilesInArchive(
                            originalZipPath=path, preserveArchiveContent=True)

        except Exception as e:
            print(e)
        return "DONE!"

    def scanFile(self,path):
        # print(path)
        detectionSpace = '' 
        suspScore = 0
        isArchive = False
        hashToChk = self.getFileHash(path)
        try:
            # TODO: use os.path.splittext or other effective alternatives
            fileExtension = "."+path.split(".")[-1]
        except Exception:
            # TODO: better way to get file-extension. Prevent filename "cloaking" malware i.e. foo.txt.exe
            fileExtension = ".unknown"
            print("Internal temporary Skipped: "+path)

        if fileExtension == ".zip" or fileExtension == ".tar":
            isArchive = True

        # Time Taken: O(n) 
        # TODO: optimize using Binary search for O(log(n))
        # Signature based detection
        if hashToChk == "RR_permission_error":
            return "SKIPPED"
    
        elif hashToChk!="":
            for hash in self.__signatures:
                if hash==str(hashToChk):
                    print(self.__signatures[hash])
                    notif_str = "Xylent taking action against detected malware "+ path
                    suspScore+=100
                    detectionSpace = "SignatureBased: " + self.__signatures[hash]
            # YARA RULES DETECTION
            if not isArchive and suspScore==0:
                try:
                    matches = self.peid_rules.match(path)
                    if matches:
                        for match in matches:
                            if 'score' in match.meta:
                                suspScore += int(match.meta['score'])
                            else:
                                # ⚠ Better scoring mechanism needed, if no score is provided ⚠
                                suspScore+=20
                            # print("YARA: "+str(match))
                            notif_str = "Xylent is taking action against detected malware "+ path
                            detectionSpace += " Yara: "+ str(match)
                        # return "aeicar!"
                except Exception as e:
                    print("sKIPPED!")

        if not isArchive and suspScore >= 70:
            # from plyer import notification
            # notification.notify(
            #     title="Malware Detected",
            #     message=notif_str,
            #     # displaying time
            #     timeout=2
            # )
            from notifypy import Notify
            notification = Notify()
            notification.title = "Malware Detected"
            notification.message = notif_str
            notification.send()
            self.quar.quarantine(path,detectionSpace)
            # If the file is an archive
            # Check for preserving setting
        
        if isArchive:
            self.handleArchives(path)

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
                    # print(verdict+" detected!"+" for "+files)
                    scanReport[files] = verdict
                elif verdict == "SKIPPED":
                    scanReport[files] = "SKIPPED"
                elif verdict == "":
                    # print("Verdict: SAFE"+verdict+" for "+files)
                    scanReport[files] = "SAFE"
        return scanReport
