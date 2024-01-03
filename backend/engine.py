import os
import yara
from flask import request,Flask,Response
from scanner import Scanner
from suspiciousWPDetector import SuspiciousWPDetector
from systemWatcher import systemWatcher
import threading
# Compile ato executable with: pyinstaller -F engine.py --hidden-import pywin32 --hidden-import notify-py --uac-admin
app = Flask(__name__)

# Global Variables
SYSTEM_DRIVE  =  os.path.expandvars("%systemdrive%")
VIRUSSHARE_PATH = "./rules/virusshare.txt"
SHA256_PATH = "./rules/sha256_db.txt"
MD5_PATH = "./rules/md5_db.txt"
SHA1_PATH = "./rules/sha1_db.txt"
TLSH_PATH = "./rules/tlsh_db.txt"
SSDEEP_PATH = "./rules/malshare.txt"
sha256_signatures_data = {}
md5_signatures_data = {}
sha1_signatures_data = {}
tlsh_signatures_data = {}
ssdeep_signatures_data = {}
virusshare_md5_signatures_data = {}
# Global variable to store compiled YARA rules
compiled_rules = {}
# Load virusshare.txt MD5 signatures
with open(SSDEEP_PATH, 'r') as f:
    temp = f.read().split("\n")
    f.close()

for i in range(len(temp)):
    ssdeep_signatures_data[temp[i]] = ""  # Set the value to an empty string, as there is no additional information
# Load virusshare.txt MD5 signatures
with open(VIRUSSHARE_PATH, 'r') as f:
    temp = f.read().split("\n")
    f.close()

for i in range(len(temp)):
    virusshare_md5_signatures_data[temp[i]] = ""  # Set the value to an empty string, as there is no additional information
# Load SHA256 signatures
with open(SHA256_PATH, 'r') as f:
    temp = f.read().split("\n")
    f.close()

for i in range(len(temp)):
    sha256_signatures_data[temp[i].split(":")[0]] = temp[i].split(":")[1]
# Load MD5 signatures
with open(MD5_PATH, 'r') as f:
    temp = f.read().split("\n")
    f.close()

for i in range(len(temp)):
    md5_signatures_data[temp[i].split(":")[0]] = ""  # Set the value to an empty string, as there is no additional information
# Load SHA256 signatures
with open(SHA1_PATH, 'r') as f:
    temp = f.read().split("\n")
    f.close()

for i in range(len(temp)):
    sha1_signatures_data[temp[i].split(":")[0]] = temp[i].split(":")[1]
#Load TLSH signatures
with open(TLSH_PATH, 'r') as f:
    temp = f.read().split("\n")
    f.close()

for i in range(len(temp)):
    tlsh_signatures_data[temp[i].split(":")[0]] = ""  # Set the value to an empty string, as there is no additional information
print("Hash Signatures loaded!")

yara_folder_path = "signature-base/yara"
compiled_rules = {}

def compile_yara_rule(rule_file):
    try:
        return yara.compile(filepath=rule_file)
    except yara.Error as e:
        print(f"Error compiling YARA rule from {rule_file}: {e}")
        return None

def load_yara_rules(folder_path):
    from concurrent.futures import ThreadPoolExecutor, as_completed

    rule_files = get_yara_rule_files(folder_path)
    total_files = len(rule_files)
    progress_per_file = 100 / total_files
    compiled_rules = {}

    max_workers = min(5, total_files)  # Set max_workers dynamically
    chunk_size = total_files // 20  # Experiment with the chunk size

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(compile_yara_rule, rule_file) for rule_file in rule_files]

        for i, future in enumerate(as_completed(futures)):
            try:
                rule = future.result()
                if rule is not None:
                    compiled_rules[rule_files[i]] = rule
            except Exception as e:
                # Handle exceptions during rule compilation (e.g., log the error)
                print(f"Error compiling rule {rule_files[i]}: {str(e)}")

            # Update progress after processing a chunk
            if (i + 1) % chunk_size == 0 or i == total_files - 1:
                progress_value = int((i + 1) * progress_per_file)
                print(f"Loading: {progress_value}%")

    return compiled_rules

def get_yara_rule_files(folder_path):
    rule_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith((".yara", ".yar", ".rule")):
                rule_files.append(os.path.join(root, file))
    return rule_files

def loading_complete(compiled_rules):
    # Do whatever you need with the compiled_rules
    print("Loading complete!")
    print(compiled_rules)

def load_yara_rules_in_thread():
    global compiled_rules
    with app.app_context():
        compiled_rules = load_yara_rules(yara_folder_path)
        loading_complete(compiled_rules)
# Call load_yara_rules_in_thread to initiate the loading process in a separate thread
load_yara_rules_in_thread()
with app.app_context():
    yara_rules = compiled_rules
# Create the Scanner instance with Yara rules
XylentScanner = Scanner(sha256_signatures=sha256_signatures_data, md5_signatures=md5_signatures_data, tlsh_signatures=tlsh_signatures_data, sha1_signatures=sha1_signatures_data, yara_rules=yara_rules, virusshare_md5_signatures=virusshare_md5_signatures_data, ssdeep_signatures=ssdeep_signatures_data, rootPath=app.root_path)
def startSystemWatcher(thread_resume):
    thread_resume = threading.Event()
    thread_resume.set()
    systemWatcher(XylentScanner,SYSTEM_DRIVE,thread_resume)
thread_resume = threading.Event()
realTime_thread = threading.Thread(
    target=startSystemWatcher,args=(thread_resume,))
realTime_thread.start()

@app.route("/setUserSetting", methods=['POST'])
def setUserSetting():
    data = request.json
    SETTING = data['setting']
    VALUE = data['value']

    print(f"Received setting: {SETTING}, value: {VALUE}")

    if SETTING == "Real Time Protection":
        if VALUE == True:
            print("Starting Real-time protection thread")
            # Start (Real-time protection)[RTP] thread to restore file
            thread_resume.set()
        else:
            print("Stopping Real-time protection thread")
            # Stop (Real-time protection)[RTP] thread
            thread_resume.clear()

    return "Config Applied!"

@app.route("/getActiveProcesses",methods=['GET'])
def activeProcess():
    import subprocess
    cmd = r'powershell "gps | where {$_.MainWindowTitle } | select ProcessName,Description,Id,Path'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    ans = []
    for line in proc.stdout:
        if not line.decode()[0].isspace():
            print(line.decode().rstrip())
            ans.append(line.decode().rstrip())
    return ans

@app.route("/getStartUpItems",methods=['GET'])
def startupItems():
    import subprocess
    # cmd = 'wmic startup list brief'
    # cmd = "reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
    cmd = r"reg query HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    data = []
    for line in proc.stdout:
        data.append(line.decode().lstrip().rstrip())
    data = list(filter(None, data))
    print(data)
    data.remove("HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\StartupApproved\\Run")

    # Preprocess
    processName = []
    temp = []
    # print("Length of data "+str(len(data)))
    for line in data:
        processes = line.split()
        # print(processes)
        pName = ''
        enable = ''
        score = 0
        detect = SuspiciousWPDetector()
        for name in processes:
            if not "REG_BINARY" in name and name[0]!='0':
                pName+=name+' '
            if name[0]=='0' and len(name)==24:
                if name[1]=='2':
                    enable = True
                elif name[1]=='3':
                    enable = False
                verdict = detect.classify(pName.rstrip())
        processName.append([pName.rstrip(),enable,verdict])
    # print(processName)
    return processName

@app.route("/toggleItemsForStartup", methods=['POST'])
def toggleStartupItems():
    import winreg
    location = winreg.HKEY_CURRENT_USER
    myKey = winreg.OpenKeyEx(
        location, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\StartupApproved\\Run", 0, winreg.KEY_SET_VALUE)
    # PATH = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\StartupApproved\\Run\\ScreenRec"
    data = request.json
    PATH = data["val"].rstrip()
    TYPE = winreg.REG_BINARY
    if(data["toggleTo"]):
        # Startup enabled
        ENABLE_VALUE = b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    else:
        # Startup disabled
        ENABLE_VALUE = b'\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    winreg.SetValueEx(myKey, PATH, 0, TYPE, ENABLE_VALUE)
    return "done"

@app.route("/initiateScans", methods=['GET','POST'])
def scans():
    data = request.json
    SCAN_TYPE = data['scanType']
    print(SCAN_TYPE)
    # Intialize scanner object
    # https://peps.python.org/pep-0635/
    SCAN_LOCATIONS = []
    if SCAN_TYPE=="Quick":
        # TODO: Add paths based on the platform, i.e. windows,linux,macos
        AppdataPath = R"C:\Users\$USERNAME\AppData"
        tempPath = R"${TEMP}"
        desktopPath = R"%UserProfile%\Desktop"
        temp = os.path.expandvars(tempPath)
        Appdata = os.path.expandvars(AppdataPath)
        desktop = os.path.expandvars(desktopPath)
        downloadPath = R"%UserProfile%\Downloads"
        downloads = os.path.expandvars(downloadPath)
        SCAN_LOCATIONS = [Appdata,temp]
        
    elif SCAN_TYPE=="Full":
        # Full Scan
        pass
    elif SCAN_TYPE=="Custom":
        # Custom
        SCAN_LOCATIONS = data['customScanFiles']
    else:
        print("Invalid Scan Type")

    print(SCAN_LOCATIONS)
    scanReport = XylentScanner.scanFolders(location=SCAN_LOCATIONS)
    return scanReport

@app.route("/quarFile",methods=['POST'])
def quarFile():
    data = request.json
    originalPath = data["originalPath"]
    detectionSpace = data['detectionSpace']
    XylentScanner.quar.quarantine(originalPath, detectionSpace)
    return "Done!"

@app.route("/restoreFile",methods=['POST'])
def restoreFile():
    data = request.json
    originalPath = data["originalPath"]
    # Pause (Real time protection)[RTP] thread to restore file
    thread_resume.clear()
    XylentScanner.quar.restore(originalPath)
    # Start RTP thread after restore complete
    thread_resume.set()
    return "Done"

@app.route("/removeFile", methods=['POST'])
def removeFile():
    data = request.json
    originalPath = data["originalPath"]
    # No need to pause RTP thread as quarantine path is always excluded
    XylentScanner.quar.remove(originalPath)
    return "Done"

def addFirewallRules(url):
    import requests
    import subprocess
    import ipaddress
    try:
        response = requests.get(url).text
        ips = response.split("\n")
        rule = "netsh advfirewall firewall delete rule name='XYLENT_AV_IP_RULE'"
        subprocess.run(['Powershell', '-Command', rule])

        for ip in ips:
            if ip and ip[0] != '!' and "#" not in ip:
                try:
                    ip_object = ipaddress.ip_address(ip)
                    rule = "netsh advfirewall firewall add rule name='XYLENT_AV_IP_RULE' Dir=Out Action=Block RemoteIP="+ip.rstrip()
                    # print(rule)
                    process = subprocess.run(
                        ['Powershell', '-Command', rule], stdout=subprocess.PIPE, encoding='utf-8')
                    realtime_output = process.stdout
                    if realtime_output == '' and process.poll() is not None:
                        break
                    if realtime_output:
                        yield f'data: {ip+" "+realtime_output.strip()} \n\n'
                except Exception as e:
                    yield f'data: {e} \n\n'
    except requests.exceptions.RequestException as e:
        yield f'data: Network Down! \n\n'

def SSEstream(funcToStream, url=None):
    if(url):
        return Response(funcToStream(url), mimetype='text/event-stream')
    else:
        return Response(funcToStream(), mimetype='text/event-stream')

def cleanJunk():
    # Remove temp files older than 24hrs
    import time
    import shutil
    localTempPath = R"${TEMP}"
    windowsTempPath = SYSTEM_DRIVE + r"\Windows\Temp"
    prefetchPath = SYSTEM_DRIVE + r"\Windows\Prefetch"
    now = time.time()
    size = 0
    root = [prefetchPath, os.path.expandvars(localTempPath), windowsTempPath]
    temp_list = []
    for target in root:
        try:
            for content in os.listdir(target):
                age = now-os.stat(os.path.join(target, content)).st_mtime
                if age/3600 >= 24:
                    size = os.stat(os.path.join(target, content)).st_size
                    temp_list.append(os.path.join(target, content))
                    yield f'data: {"Removing File: "+ os.path.join(target,content)+ " Size: "+str(size)} \n\n'
        except PermissionError:
            print(target)

    for file in temp_list:
        try:
            os.remove(file)
        except:
            try:
                shutil.rmtree(file, ignore_errors=True)
            except:
                print("Already in use "+file)

@app.route("/cleanJunk", methods=['POST'])
def streamTemCleaningtoFrontend():
    return SSEstream(cleanJunk)

@app.route('/addFirewallRules',methods=['GET','POST'])
def streamFirewallRulestoFrontend():
    data = request.json
    return SSEstream(addFirewallRules,data['link'])
            
@app.route('/executeCommand',methods=['POST'])
def executeCommand():
    import subprocess
    data = request.json
    program = data['commandData']["program"]
    command = data['commandData']["command"]
    subprocess.run([program,'-Command',command])
    return "Done"
    
@app.route("/launchProgram", methods=['POST'])
def launchProgram():
    data = request.json
    PROGRAM_PATH = data['programPath']
    import subprocess
    if(os.path.exists(PROGRAM_PATH)):
        try:
            subprocess.Popen(PROGRAM_PATH)
            return "Done!"
        except Exception as e:
            print(e)
            return str(e)
    else:
        return "Cannot open: " + PROGRAM_PATH
    
if __name__ == '__main__':
   app.run(debug=False)
