import os
from queue import Queue
import subprocess
from concurrent.futures import ThreadPoolExecutor
import threading
import shutil

verdict_queue = Queue()

def systemWatcher(XylentScanner, thread_resume):
    monitor_exe_path = os.path.abspath('.\\monitor\\target\\debug\\monitor.exe')
    subprocess.Popen([monitor_exe_path])

    output_txt_path = "output.txt"
    output_copy_path = "output_copy.txt"

    def scan_path(path):
        try:
            verdict = XylentScanner.scanFile(path)
            verdict_queue.put(verdict)  # Put the result in the queue
        except Exception as e:
            print(e)
            print(f"Error processing {path}")

    def scan_changes():
        last_position = 0
        with ThreadPoolExecutor(max_workers=10000) as executor:
            while thread_resume.is_set():
                try:
                    # Kopya dosyayı oluştur
                    shutil.copy(output_txt_path, output_copy_path)

                    with open(output_copy_path, "r") as file:
                        file.seek(last_position)
                        changes = file.readlines()

                        if not changes:
                            # No new data, block until new lines are added
                            continue

                        # Collect paths to process simultaneously
                        paths_to_process = []
                        for change in changes:
                            path_to_scan = os.path.abspath(change.strip())
                            print(path_to_scan)

                            if os.path.exists(path_to_scan):
                                paths_to_process.append(path_to_scan)
                            else:
                                print(f"File does not exist: {path_to_scan}")

                        # Process all collected paths simultaneously using ThreadPoolExecutor
                        for path in paths_to_process:
                            try:
                                verdict = XylentScanner.scanFile(path)
                                verdict_queue.put(verdict)  # Put the result in the queue
                            except Exception as e:
                                print(e)
                                print(f"Error scanning {path}")

                        # Update the last position to the end of the file
                        last_position = file.tell()
                except Exception as e:
                    print(e)

    # Start the scanning process in a separate thread
    threading.Thread(target=scan_changes).start()

    print("RTP waiting to start...")
