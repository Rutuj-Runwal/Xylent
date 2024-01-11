import os
from queue import Queue
import subprocess
import threading

verdict_queue = Queue()

def systemWatcher(XylentScanner, SYSTEM_DRIVE, thread_resume):

    # Run the monitor.exe in a separate process
    monitor_exe_path = os.path.abspath('.\\monitor\\x64\\Debug\\monitor.exe')
    subprocess.Popen([monitor_exe_path, os.path.abspath(SYSTEM_DRIVE)])

    output_txt_path = "output.txt"
    last_position = 0

    while thread_resume.is_set():
        try:
            with open(output_txt_path, "r") as file:
                file.seek(last_position)
                changes = file.readlines()

                if not changes:
                    # No new data, block until new lines are added
                    file.readline()

                    # Move to the end of the file for the next iteration
                    last_position = file.tell()
                else:
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

                    # Update the last position to the end of the file
                    last_position = file.tell()
        except Exception as e:
            print(e)

    print("RTP waiting to start...")
