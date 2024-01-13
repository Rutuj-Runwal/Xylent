import os
from queue import Queue
import subprocess
from concurrent.futures import ThreadPoolExecutor
import threading
import shutil
import psutil

verdict_queue = Queue()

def get_all_running_files():
    running_files = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        running_files.append(proc.info['exe'])
    return running_files

def systemWatcher(XylentScanner, thread_resume):
    if os.path.exists(output_txt_path):
            os.remove(output_txt_path)
    if os.path.exists(output_copy_path):
            os.remove(output_copy_path)
    monitor_exe_path = os.path.abspath('.\\monitor\\target\\debug\\monitor.exe')
    subprocess.Popen([monitor_exe_path])

    output_txt_path = "output.txt"
    output_copy_path = "output_copy.txt"

    def scan_changes():
        last_position = 0
        with ThreadPoolExecutor(max_workers=10000) as executor:
            while thread_resume.is_set():
                try:
                    # Get all running files
                    running_files = get_all_running_files()

                    # Copy the output.txt file
                    shutil.copy(output_txt_path, output_copy_path)

                    with open(output_copy_path, "r") as file:
                        file.seek(last_position)
                        changes = file.readlines()

                    if changes:
                        for change in changes:
                            path_to_scan = os.path.abspath(change.strip())
                            print(path_to_scan)

                            if os.path.exists(path_to_scan):
                                running_files.append(path_to_scan)
                            else:
                                print(f"File does not exist: {path_to_scan}")

                    # Process all collected paths simultaneously using ThreadPoolExecutor
                    futures = [executor.submit(XylentScanner.scanFile, path) for path in running_files]
                    for future in futures:
                        try:
                            verdict = future.result()
                            verdict_queue.put(verdict)  # Put the result in the queue
                        except Exception as e:
                            print(e)

                    # Update the last position to the end of the file
                    last_position = file.tell()

                except Exception as e:
                    print(e)

    # Start the scanning process in a separate thread
    threading.Thread(target=scan_changes).start()

    print("RTP waiting to start...")
