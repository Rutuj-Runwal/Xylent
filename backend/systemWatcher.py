import os
import ctypes
import subprocess
from parseJson import ParseJson

def scan_and_update(XylentScanner, XYLENT_SCAN_CACHE, pathToScan):
    try:
        # Perform the file scanning operation
        verdict = XylentScanner.scanFile(pathToScan)
        print("Scanned:", pathToScan, "Verdict:", verdict)

        # Update the scan cache with the verdict for the scanned file
        XYLENT_SCAN_CACHE.setVal(pathToScan, verdict)
    except Exception as e:
        # Handle exceptions during the scanning process
        print("Error during scanning:", e)

def systemWatcher(XylentScanner, SYSTEM_DRIVE, thread_resume):
    # Initialize the cache for scanned files
    XYLENT_SCAN_CACHE = ParseJson('./config', 'xylent_scancache', {})
    XYLENT_CACHE_MAXSIZE = 500000  # 500KB

    # Specify the name of the DLL file (e.g., monitor_dll.dll)
    dll_name = "monitor.dll"

    # Specify the full path of the DLL file (in the current folder under the monitordebug folder)
    dll_path = os.path.join(os.getcwd(), "monitordebug", dll_name)

    # Load the DLL
    my_dll = ctypes.CDLL(dll_path)

    # Call the StartMonitoring function
    monitored_path = SYSTEM_DRIVE + "\\"
    my_dll.StartMonitoring.argtypes = [ctypes.c_wchar_p]
    my_dll.StartMonitoring.restype = None
    my_dll.StartMonitoring(monitored_path)

    while thread_resume.wait():
        try:
            # Run the monitor.dll and capture its output in real-time
            with subprocess.Popen([dll_path], stdout=subprocess.PIPE, text=True) as process:
                for line in process.stdout:
                    pathToScan = line.strip()
                    print("Path to Scan:", pathToScan)

                    if pathToScan:
                        # Call the scanning function
                        scan_and_update(XylentScanner, XYLENT_SCAN_CACHE, pathToScan)
        except Exception as e:
            # Handle exceptions during the scanning process
            print("Error during scanning loop:", e)

        # Check if the scan cache has exceeded the maximum size
        if os.path.getsize(XYLENT_SCAN_CACHE.PATH) >= XYLENT_CACHE_MAXSIZE:
            # Purge the scan cache if the size exceeds the limit
            XYLENT_SCAN_CACHE.purge()
            print("Purging")

    # Display a message when the systemWatcher is waiting to start
    print("RTP waiting to start...")
