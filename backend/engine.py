import os
import yara
from flask import request,Flask,Response
from scanner import Scanner
from suspiciousWPDetector import SuspiciousWPDetector
from systemWatcher import systemWatcher
import threading
# Compile to executable with: pyinstaller -F engine.py --hidden-import pywin32 --hidden-import plyer.platforms.win.notification --uac-admin
app = Flask(__name__)

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
    if getattr(sys, 'frozen',False):
            # Current Path - For Frozen executable[prod]
            BASE_PATH  = "./"
    else:
        BASE_PATH = app.root_path
        
    print(BASE_PATH)
    yaraRules = ""
    dummy = ""
    rule_count = 0
    # for yara_rule_directory in self.yara_rule_directories:
    yara_rule_directory = os.path.join(
        BASE_PATH, "signature-base/yara".replace("/", os.sep))
    if not os.path.exists(yara_rule_directory):
        return "Cannot find signature base"
    if not os.path.exists(BASE_PATH+'/compiledRules'):
        for root, directories, files in os.walk(yara_rule_directory, followlinks=False):
            for file in files:
                try:
                    # Full Path
                    yaraRuleFile = os.path.join(root, file)

                    # Skip hidden, backup or system related files
                    if file.startswith(".") or file.startswith("~") or file.startswith("_"):
                        continue

                    # Extension
                    extension = os.path.splitext(file)[1].lower()

                    # Skip all files that don't have *.yar or *.yara extensions
                    if extension != ".yar" and extension != ".yara":
                        continue

                    with open(yaraRuleFile, 'r') as yfile:
                        yara_rule_data = yfile.read()

                    # Add the rule
                    rule_count = rule_count+1
                    yaraRules += yara_rule_data

                except Exception as e:
                    print("Error reading signature file %s" % (yaraRuleFile))
        try:
            compiledRules = yara.compile(source=yaraRules, externals={
                'filename': dummy,
                'filepath': dummy,
                'extension': dummy,
                'filetype': dummy,
                'md5': dummy,
                'owner': dummy,
            })
            compiledRules.save(BASE_PATH+"/compiledRules")
            print("Initialized %d Yara rules" % rule_count)
            return "Initialized" + rule_count +" Yara rules"
        except Exception as e:
            return "Error during YARA rule compilation ERROR: - please fix the issue in the rule set"
with app.app_context():
    compileYaraSigs()

XylentScanner = Scanner(signatures=signaturesData, rootPath=app.root_path)


def startSystemWatcher(thread_resume):
    thread_resume.set()
    systemWatcher(XylentScanner,thread_resume)

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
        # print(line.decode().rstrip().split(" "))
        data.append(line.decode().lstrip().rstrip())
    data = list(filter(None, data))
    print(data)
    data.remove("HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\StartupApproved\\Run")
    # print("---------------------")
    # print(data[11].split())
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

@app.route("/loggedInUsername", methods=['GET'])
def getUsername():
    import getpass.getuser as getuser
    return getuser()

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
    if SCAN_TYPE=="Quick":
        # TODO: Add paths based on the platform, i.e. windows,linux,macos
        # user = getUsername()
        AppdataPath = R"C:\Users\$USERNAME\AppData"
        tempPath = R"${TEMP}"
        desktopPath = R"%UserProfile%\Desktop"
        temp = os.path.expandvars(tempPath)
        # print(temp)
        Appdata = os.path.expandvars(AppdataPath)
        desktop = os.path.expandvars(desktopPath)
        # REMOVE - TEMP ONLY !!!!!!!!!
        tPath = R"%UserProfile%\Downloads\Test\TestX"
        testPath = os.path.expandvars(tPath)
        # REMOVE - TEMP ONLY !!!!!!!!!
        # x = time.time()
        scanReport = XylentScanner.scanFolders(location=[testPath])
        # y = time.time()
        # print("--------------")
        # print("Time taken:",y-x)
        return scanReport

    elif SCAN_TYPE=="Full":
        # Full Scan
        pass
    elif SCAN_TYPE=="Custom":
        # Custom
        pass
    else:
        print("Invalid Scan Type")

@app.route("/deviceStats", methods=['POST'])
def deviceStats():
    import shutil
    from plyer import battery, devicename, wifi
    print(battery.status)
    if(wifi.is_enabled()):
        print(wifi.is_connected())

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
    windowsTempPath = "C:\Windows\Temp"
    prefetchPath = "C:\Windows\Prefetch"
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
