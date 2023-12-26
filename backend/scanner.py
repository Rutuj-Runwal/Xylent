import hashlib
import os
import tlsh
from quarantineThreats import Quarantine

class Scanner:
    def __init__(self, sha256_signatures, md5_signatures, tlsh_signatures, rootPath, yara_rules):
        self.__sha256_signatures = sha256_signatures
        self.__md5_signatures = md5_signatures
        self.__tlsh_signatures = tlsh_signatures
        self.__rootPath = rootPath
        self.yara_rules = yara_rules  # Replace with your actual YARA rules
        self.quarantineData = {
            'configFileName': 'quar_info',
            'configFilePath': os.path.join(self.__rootPath, 'config'),
            'defaults': {}
        }
        print("-----Scanner Initialized-----")
        self.quar = Quarantine(self.quarantineData)

        # Read excluded rule names from the file
        excluded_rules_path = os.path.join(self.__rootPath, 'excluded', 'excluded_rules.txt')
        with open(excluded_rules_path, "r") as file:
            self.excluded_rules = file.read()

    def getFileHash(self, path):
        hash = ""
        try:
            with open(path, 'rb') as f:
                bytes = f.read()
                hash = hashlib.sha256(bytes).hexdigest()
            if hash != "":
                return hash
        except (PermissionError, OSError):
            print("Permission Error")
            return "XYLENT_PERMISSION_ERROR"

    def getMD5Hash(self, path):
        hash = ""
        try:
            with open(path, 'rb') as f:
                bytes = f.read()
                hash = hashlib.md5(bytes).hexdigest()
            if hash != "":
                return hash
        except (PermissionError, OSError):
            print("Permission Error")
            return "XYLENT_PERMISSION_ERROR"

    def getTLSHHash(self, path):
        hash = ""
        try:
            with open(path, 'rb') as f:
                bytes = f.read()
                hash = tlsh.hash(bytes)
            if hash != "":
                return hash
        except (PermissionError, OSError):
            print("Permission Error")
            return "XYLENT_PERMISSION_ERROR"

    def verifyExecutableSignature(self, path):
        import subprocess
        import time
        import datetime
        cmd = " " + f'"{path}"'
        command = "(Get-AuthenticodeSignature" + cmd + ").Status"
        process = subprocess.run(['Powershell', '-Command', command], stdout=subprocess.PIPE, encoding='utf-8')
        now = time.time()
        ageInSec = now - os.stat(path).st_mtime
        age = str(datetime.timedelta(seconds=ageInSec))
        if process.stdout.strip() == "HashMismatch" or process.stdout.strip() == "UnknownError":
            return {'score': 80, 'age': age}
        elif process.stdout.strip() == "NotTrusted":
            return {'score': 70, 'age': age}
        elif process.stdout.strip() == "NotSigned":
            return {'score': 30, 'age': age}
        else:
            return {'score': 0, 'age': age}

    def handleArchives(self, path):
        print("Handling Archive!!")
        import shutil
        try:
            archiveExtractPath = "./scanExtracts"
            if archiveExtractPath.split("/")[1] in path:
                print("Skipped to avoid recursion. Depth=1 for scanning archives!")
                return "DONE!"
            else:
                if not os.path.exists(archiveExtractPath):
                    os.mkdir(archiveExtractPath)
                shutil.unpack_archive(path, archiveExtractPath)
                verdicts = self.scanFolders(archiveExtractPath)
                if "[S]" or "[Y]" in verdicts:
                    if os.path.exists(archiveExtractPath):
                        print("Malware detected in archive")
                        from notifypy import Notify
                        notification = Notify()
                        # Set notification properties
                        notification.title = "Archive Repaired"
                        notification.message = "Archive with malicious content repaired. Malware removed, Safe content Preserved!"
                        notification.send()
                        self.quar.quarantineFilesInArchive(originalZipPath=path, preserveArchiveContent=True)

        except Exception as e:
            print(e)
        return "DONE!"
    def scanFile(self, path):
        detectionSpace = "SAFE"
        suspScore = 0
        isArchive = False
        try:
            fileExtension = os.path.splitext(path)[1]
            hashToChk = self.getFileHash(path)

            if hashToChk == "XYLENT_PERMISSION_ERROR":
                return "SKIPPED"

            if fileExtension == ".zip" or fileExtension == ".tar":
                isArchive = True

            if not isArchive and (fileExtension == ".exe" or fileExtension == ".msi"):
                # ... (existing code)

             if hashToChk != "" and suspScore < 70:
                # TLSH BASED DETECTION
                tls_match_found = False
                if not isArchive:
                    try:
                        tlsh_hash = self.getTLSHHash(path)
                        for tlsh_sig in self.__tlsh_signatures:
                            if tlsh.match(tlsh_sig, tlsh_hash):
                                print(self.__tlsh_signatures[tlsh_sig])
                                detectionSpace = "[T]" + self.__tlsh_signatures[tlsh_sig]
                                tls_match_found = True
                                # Set suspScore to 100 or any other value as needed
                                suspScore = 100
                                break
                    except Exception as e:
                        print(f"Error during TLSH matching: {e}")

            # ... (existing code)

            return detectionSpace
        except Exception as e:
            print(e)
            return "SKIPPED"

    def scanFolders(self, location):
        directories = []
        if isinstance(location, list):
            for target in location:
                for (dirpath, dirnames, filenames) in os.walk(target):
                    directories += [os.path.join(dirpath, file) for file in filenames]
        elif isinstance(location, str):
            for (dirpath, dirnames, filenames) in os.walk(location):
                directories += [os.path.join(dirpath, file) for file in filenames]

        scanReport = {}
        for files in directories:
            verdict = self.scanFile(files)
            if verdict:
                print("Verdict is: " + verdict)
                scanReport[files] = verdict
        return scanReport
