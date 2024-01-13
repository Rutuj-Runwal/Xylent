import os
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import threading
import subprocess
import psutil
import shutil
import time

verdict_queue = Queue()

def get_all_running_files():
    running_files = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        running_files.append(proc.info['exe'])
    return running_files

def systemWatcher(XylentScanner, thread_resume):
    output_txt_path = "output.txt"
    output_copy_path = "output_copy.txt"

    if os.path.exists(output_txt_path):
        os.remove(output_txt_path)
    if os.path.exists(output_copy_path):
        os.remove(output_copy_path)
    monitor_exe_path = os.path.abspath('.\\monitor\\target\\debug\\monitor.exe')
    subprocess.Popen([monitor_exe_path])

    scanned_files = set()  # Keep track of scanned files
    last_cleanup_time = time.time()  # Initialize the last cleanup time

    def scan_changes():
        nonlocal scanned_files, last_cleanup_time  # Use the scanned_files and last_cleanup_time from the outer function
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

                            if os.path.exists(path_to_scan) and path_to_scan not in scanned_files:
                                # Process the path using ThreadPoolExecutor
                                executor.submit(XylentScanner.scanFile, path_to_scan)
                                scanned_files.add(path_to_scan)

                    # Update the last position to the end of the file
                    last_position = file.tell()

                    # Check if it's time to clean up the scanned_files set (every 60 seconds)
                    current_time = time.time()
                    if current_time - last_cleanup_time >= 60:
                        scanned_files.clear()  # Clear the set
                        last_cleanup_time = current_time

                except Exception as e:
                    print(e)
                
    # Start the scanning process in a separate thread
    threading.Thread(target=scan_changes).start()

    print("RTP waiting to start...")
