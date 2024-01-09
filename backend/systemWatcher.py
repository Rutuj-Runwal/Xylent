import os
import ctypes
from parseJson import ParseJson

def systemWatcher(XylentScanner, SYSTEM_DRIVE, thread_resume, pathToScan):
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
    monitored_path = SYSTEM_DRIVE
    my_dll.StartMonitoring.argtypes = [ctypes.c_wchar_p]
    my_dll.StartMonitoring.restype = None
    my_dll.StartMonitoring(monitored_path)

    # Continuously monitor and scan files
    while thread_resume.wait():
        try:
            # Check if there is a file path to scan
            if pathToScan:
                # Perform the file scanning operation (replace XylentScanner.scanFile with your actual scanning logic)
                verdict = XylentScanner.scanFile(pathToScan)
                
                # Update the scan cache with the verdict for the scanned file
                XYLENT_SCAN_CACHE.setVal(pathToScan, verdict)
        except Exception as e:
            # Handle exceptions during the scanning process
            print(e)

        # Check if the scan cache has exceeded the maximum size
        if os.path.getsize(XYLENT_SCAN_CACHE.PATH) >= XYLENT_CACHE_MAXSIZE:
            # Purge the scan cache if the size exceeds the limit
            XYLENT_SCAN_CACHE.purge()
            print("Purging")

    # Display a message when the systemWatcher is waiting to start
    print("RTP waiting to start...")
