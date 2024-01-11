import os
from queue import Queue
import subprocess

verdict_queue = Queue()

def systemWatcher(XylentScanner, SYSTEM_DRIVE, thread_resume):

    # Run the monitor.exe in a separate process
    monitor_exe_path = os.path.abspath('.\\monitor\\x64\\Debug\\monitor.exe')
    subprocess.Popen([monitor_exe_path, os.path.abspath(SYSTEM_DRIVE)])

    while thread_resume.is_set():
        try:
            # Specify the path to output.txt relative to monitor.exe
            output_txt_path = os.path.abspath('.\\monitor\\x64\\Debug\\output.txt')

            with open(output_txt_path, "r") as file:
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
