import os
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import threading
import subprocess
import psutil
import shutil

verdict_queue = Queue()

def get_all_running_files():
    running_files = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        running_files.append(proc.info['exe'])
    return running_files

def systemWatcher(XylentScanner,thread_resume):
    output_txt_path = "output.txt"
    output_copy_path = "output_copy.txt"

    if os.path.exists(output_txt_path):
        os.remove(output_txt_path)
    if os.path.exists(output_copy_path):
        os.remove(output_copy_path)
    monitor_exe_path = os.path.abspath('.\\monitor\\target\\debug\\monitor.exe')
    subprocess.Popen([monitor_exe_path])

    def scan_changes():
        last_position = 0
        with ThreadPoolExecutor(max_workers=10000) as executor:
            while thread_resume.is_set():
                try:
                    # Copy the content of output.txt to output_copy.txt
                    shutil.copy(output_txt_path, output_copy_path)

                    with open(output_copy_path, "r") as file:
                        file.seek(last_position)
                        changes = file.readlines()

                    if changes:
                        for change in changes:
                            path_to_scan = os.path.abspath(change.strip())
                            print(path_to_scan)

                            if os.path.exists(path_to_scan):
                                # Process the path using ThreadPoolExecutor
                                executor.submit(XylentScanner.scanFile, path_to_scan)

                    # Update the last position to the end of the file
                    last_position = file.tell()

                except Exception as e:
                    print(e)

    # Start the scanning process in a separate thread
    threading.Thread(target=scan_changes).start()

    print("RTP waiting to start...")
