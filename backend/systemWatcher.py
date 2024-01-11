import os
import ctypes
import threading
from queue import Queue

verdict_queue = Queue() 

def systemWatcher(XylentScanner, SYSTEM_DRIVE, thread_resume):

    # Load the DLL from the monitordebug directory
    monitor_dll_path = os.path.abspath('.\\monitor\\x64\\Debug\\monitor.dll')
    monitor_dll = ctypes.CDLL(monitor_dll_path)

    # Define the StartMonitoring function
    start_monitoring = monitor_dll.StartMonitoring
    start_monitoring.argtypes = [ctypes.c_wchar_p]
    start_monitoring.restype = None

    # Start monitoring the specified path in a separate thread
    monitor_thread = threading.Thread(target=start_monitoring, args=(os.path.abspath(SYSTEM_DRIVE),))
    monitor_thread.start()

    while thread_resume.is_set():
        try:
            with open("output.txt", "r") as file:
                changes = file.readlines()

            for change in changes:
                pathToScan = os.path.abspath(os.path.join(SYSTEM_DRIVE, change.strip()))
                print(pathToScan)

                try:
                    if pathToScan:
                        verdict = XylentScanner.scanFile(pathToScan)
                        verdict_queue.put(verdict)  # Put the result in the queue
                except Exception as e:
                    print(e)
                    print(f"Error processing {pathToScan}")
        except Exception as e:
            print(e)

    print("RTP waiting to start...")
