import os
from queue import Queue
import subprocess
from concurrent.futures import ThreadPoolExecutor

verdict_queue = Queue()

def systemWatcher(XylentScanner, SYSTEM_DRIVE, thread_resume):
    monitor_exe_path = os.path.abspath('.\\monitor\\x64\\Debug\\monitor.exe')
    subprocess.Popen([monitor_exe_path, os.path.abspath(SYSTEM_DRIVE)])

    output_txt_path = "output.txt"
    last_position = 0

    def scan_path(path):
        try:
            verdict = XylentScanner.scanFile(path)
            verdict_queue.put(verdict)  # Put the result in the queue
        except Exception as e:
            print(e)
            print(f"Error processing {path}")

    with ThreadPoolExecutor(max_workers=100) as executor:
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
                        # Collect paths to process simultaneously
                        paths_to_process = []
                        for change in changes:
                            path_to_scan = os.path.abspath(os.path.join(SYSTEM_DRIVE, change.strip()))
                            print(path_to_scan)

                            try:
                                if path_to_scan:
                                    paths_to_process.append(path_to_scan)
                            except Exception as e:
                                print(e)
                                print(f"Error processing {path_to_scan}")

                        # Process all collected paths simultaneously using ThreadPoolExecutor
                        executor.map(scan_path, paths_to_process)

                        # Update the last position to the end of the file
                        last_position = file.tell()
            except Exception as e:
                print(e)

    print("RTP waiting to start...")
