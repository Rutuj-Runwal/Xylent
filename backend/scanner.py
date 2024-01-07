import os
from quarantineThreats import Quarantine

class Scanner:
    def __init__(self, rootPath, yara_rules):
        self.yara_rules = yara_rules
        self.__rootPath = rootPath
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
                if "[S]" in verdicts or "[Y]" in verdicts:
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
            file_size = os.path.getsize(path)

            if fileExtension == ".zip" or fileExtension == ".tar":
                isArchive = True

            if not isArchive and suspScore < 70:
                try:
                    with open(path, 'rb') as f:
                        file_content = f.read()
                    yara_match_found = False
                    for rule_name, compiled_rule in self.yara_rules.items():
                        matches = compiled_rule.match(data=file_content)
                        for match in matches:
                            if match.rule not in self.excluded_rules:
                                # If any YARA rule matches, consider it as malware
                                print(f"YARA Rule Match: {rule_name} - {match}")
                                detectionSpace = "[Y]" + rule_name
                                yara_match_found = True
                        if yara_match_found:
                            # Set suspScore to 100 or any other value as needed
                            suspScore = 100
                            print(f"Updated suspScore: {suspScore}")
                except Exception as e:
                    print(f"Error scanning {path} with YARA rules: {e}")

            # Print the verdict
            print(f"Verdict for {path}: {detectionSpace}")

            if not isArchive and suspScore >= 70:
                notif_str = "Xylent is taking action against detected malware " + path
                from notifypy import Notify
                notification = Notify()
                notification.title = "Malware Detected"
                notification.message = notif_str
                notification.send()
                self.quar.quarantine(path, detectionSpace)
            if isArchive:
                self.handleArchives(path)

            return detectionSpace
        except Exception as e:
            print(f"Error scanning {path}: {e}")
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
