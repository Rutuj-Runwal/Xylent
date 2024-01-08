import os
import win32file
import win32con
from queue import Queue
import psutil
import concurrent.futures
from parseJson import ParseJson

FILE_ACTION_ADDED = 0x00000001
FILE_ACTION_REMOVED = 0x00000002
FILE_ACTION_MODIFIED = 0x00000003
FILE_LIST_DIRECTORY = 0x0001
FILE_NOTIFY_CHANGE_LAST_ACCESS = 0x00000020

# Initialize ParseJson
XYLENT_NEW_PROCESS_INFO = ParseJson('./config', 'new_processes.json', {})

# Add global declarations for 'printed_processes' and 'previous_list'
printed_processes = set()
previous_list = set()
results_queue = Queue()  # Define results_queue as a global variable
def systemWatcher(XylentScanner, SYSTEM_DRIVE, thread_resume):
    XYLENT_SCAN_CACHE = ParseJson('./config', 'xylent_scancache', {})

    def file_monitor():
        while thread_resume.wait():
            # File monitoring
            path_to_watch = SYSTEM_DRIVE + "\\"
            hDir = win32file.CreateFile(
                path_to_watch,
                FILE_LIST_DIRECTORY,
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
                win32con.FILE_NOTIFY_CHANGE_SECURITY |
                FILE_ACTION_ADDED |
                FILE_ACTION_MODIFIED |
                FILE_ACTION_REMOVED |
                FILE_NOTIFY_CHANGE_LAST_ACCESS,
                None,
                None
            )

            for action, file in results:
                path_to_scan = os.path.join(path_to_watch, file)
                print(path_to_scan)  # Print the path for debugging purposes
                result3 = XylentScanner.scanFile(path_to_scan)
                results_queue.put(result3)  # Put the result in the queue
                XYLENT_SCAN_CACHE.setVal(path_to_scan, result3)

    # Create a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks to the executor
        monitor_thread_future = executor.submit(file_monitor)

    # Wait for all tasks to complete
    concurrent.futures.wait([monitor_thread_future])

    print("RTP waiting to start...")
