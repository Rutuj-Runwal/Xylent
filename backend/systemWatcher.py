import os
from queue import Queue
import subprocess
from concurrent.futures import ThreadPoolExecutor
import win32file
import win32con

verdict_queue = Queue()

def scan_path(XylentScanner, path):
    try:
        verdict = XylentScanner.scanFile(path)
        verdict_queue.put(verdict)
    except Exception as e:
        print(e)
        print(f"Error processing {path}")

def systemWatcher(XylentScanner, SYSTEM_DRIVE, thread_resume):
    monitor_exe_path = os.path.abspath('.\\monitor\\x64\\Debug\\monitor.exe')
    subprocess.Popen([monitor_exe_path, os.path.abspath(SYSTEM_DRIVE)])

    output_txt_path = "output.txt"
    last_position = 0

    def process_changes(changes):
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

        with ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(lambda path: scan_path(XylentScanner, path), paths_to_process)

    while thread_resume.wait():
        path_to_watch = os.path.abspath(SYSTEM_DRIVE + "\\")

        hDir = win32file.CreateFile(
            path_to_watch,
            1,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_FLAG_BACKUP_SEMANTICS,
            None
        )

        results = win32file.ReadDirectoryChangesW(
            hDir,
            1024,
            True,
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
            win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
            win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
            win32con.FILE_NOTIFY_CHANGE_SIZE |
            win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
            win32con.FILE_NOTIFY_CHANGE_SECURITY,
            None,
            None
        )

        for action, file in results:
            path_to_scan = os.path.join(path_to_watch, file)

            # Avoid unnecessary scanning based on specific paths
            if path_to_scan == "" or XylentScanner.quar.quarantine_dir in path_to_scan:
                continue

            try:
                verdict = XylentScanner.scanFile(path_to_scan)
                verdict_queue.put((path_to_scan, verdict))
            except Exception as e:
                print(e)
                print(f"{str(action)} {file} ")

        try:
            with open(output_txt_path, "r") as file:
                file.seek(last_position)
                changes = file.readlines()

                if not changes:
                    file.readline()
                    last_position = file.tell()
                else:
                    process_changes(changes)
                    last_position = file.tell()
        except Exception as e:
            print(e)

    print("RTP waiting to start...")
