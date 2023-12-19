import os
import yara
from flask import request,Flask,Response
from scanner import Scanner
from suspiciousWPDetector import SuspiciousWPDetector
from systemWatcher import systemWatcher
import threading
# Compile to executable with: pyinstaller -F engine.py --hidden-import pywin32 --hidden-import notify-py --uac-admin
app = Flask(__name__)

# Global Variables
SYSTEM_DRIVE  =  os.path.expandvars("%systemdrive%")


# Load in SHA256 signatures
PATH = "./rules/sha256_db.txt"
signaturesData = {}
with open(PATH,'r') as f:
    temp = f.read().split("\n")
    f.close()
for i in range(len(temp)):
    signaturesData[temp[i].split(":")[0]] = temp[i].split(":")[1]

print("Signatures loaded!")
# compile yara rulesets
def compileYaraSigs():
    import sys

    if getattr(sys, 'frozen', False):
        # For Frozen executable[prod]
        BASE_PATH = os.path.dirname(sys.executable)
    else:
        BASE_PATH = os.path.dirname(os.path.abspath(__file__))

    yaraRules = ""
    rule_count = 0

    yara_rule_directory = os.path.join(BASE_PATH, "signature-base/yara")
    compiled_rules_path = os.path.join(BASE_PATH, "compiledRules")

    if not os.path.exists(yara_rule_directory):
        return "Cannot find signature base"

    try:
        for root, directories, files in os.walk(yara_rule_directory, followlinks=False):
            for file in files:
                try:
                    # Full Path
                    yara_rule_file = os.path.join(root, file)

                    with open(yara_rule_file, 'r', encoding='latin-1') as yfile:
                        yara_rule_data = yfile.read()

                    # Add the rule
                    rule_count += 1
                    yaraRules += yara_rule_data + '\n'  # Add a newline between rules

                except Exception as e:
                    print("Error reading signature file %s" % (yara_rule_file))

        if not os.path.exists(compiled_rules_path):
            os.makedirs(compiled_rules_path)

        compiled_rules_file = os.path.join(compiled_rules_path, "compiledRules")
        with open(compiled_rules_file, 'w', encoding='latin-1') as f:
            f.write(yaraRules)

        compiledRules = yara.compile(filepath=compiled_rules_file)

        print("Initialized %d Yara rules" % rule_count)
        return "Initialized " + str(rule_count) + " Yara rules"
    except Exception as e:
        return "Error during YARA rule compilation ERROR: - please fix the issue in the rule set"
with app.app_context():
    compileYaraSigs()
XylentScanner = Scanner(signatures=signaturesData, rootPath=app.root_path)


def startSystemWatcher(thread_resume):
    thread_resume.set()
    systemWatcher(XylentScanner,SYSTEM_DRIVE,thread_resume)

thread_resume = threading.Event()
realTime_thread = threading.Thread(
    target=startSystemWatcher,args=(thread_resume,))
realTime_thread.start()

@app.route("/setUserSetting",methods=['POST'])
def setUserSetting():
    data = request.json
    SETTING = data['setting']
    VALUE = data['value']
    print(VALUE)
    if SETTING=="Real Time Protection":
        if VALUE==True:
            # Start (Real time protection)[RTP] thread to restore file
            thread_resume.set()
        else:
            thread_resume.clear()
            print("RTP Set!")
    return "Config Applied!"



@app.route("/getActiveProcesses",methods=['GET'])
def activeProcess():
    import subprocess
    cmd = 'powershell "gps | where {$_.MainWindowTitle } | select ProcessName,Description,Id,Path'
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
    cmd = "reg query HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
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
                        ['Powershell', '-Command', rule], stdout=subprocess.PIPE, encoding='latin-1')
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
    windowsTempPath = SYSTEM_DRIVE+"\Windows\Temp"
    prefetchPath = SYSTEM_DRIVE+"\Windows\Prefetch"
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
