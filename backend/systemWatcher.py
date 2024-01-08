import os
import win32file
import win32con
from queue import Queue
from parseJson import ParseJson

FILE_ACTION_ADDED = 0x00000001
FILE_ACTION_REMOVED = 0x00000002
FILE_ACTION_MODIFIED = 0x00000003
FILE_LIST_DIRECTORY = 0x0001
FILE_NOTIFY_CHANGE_LAST_ACCESS = 0x00000020

# Initialize ParseJson
XYLENT_NEW_PROCESS_INFO = ParseJson('./config', 'new_processes.json', {})

results_queue = Queue()  # Define results_queue as a global variable

FILE_LIST_DIRECTORY = 0x0001
FILE_NOTIFY_CHANGE_FILE_NAME = 0x0001
FILE_NOTIFY_CHANGE_DIR_NAME = 0x0002
FILE_NOTIFY_CHANGE_ATTRIBUTES = 0x0004
FILE_NOTIFY_CHANGE_SIZE = 0x0008
FILE_NOTIFY_CHANGE_LAST_WRITE = 0x0010
FILE_NOTIFY_CHANGE_SECURITY = 0x0100
FILE_NOTIFY_CHANGE_LAST_ACCESS = 0x00000020
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_SHARE_DELETE = 0x00000004
OPEN_EXISTING = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000

BUF_LEN = 1024 * (win32con.MAX_PATH + 1)

def systemWatcher(XylentScanner, SYSTEM_DRIVE, thread_resume):
    XYLENT_SCAN_CACHE = ParseJson('./config', 'xylent_scancache', {})
    dir_handle = win32file.CreateFile(
        SYSTEM_DRIVE,
        FILE_LIST_DIRECTORY,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        None,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS,
        None
    )
    try:
        while thread_resume.is_set():  # Use is_set() to check the threading event
            results = win32file.ReadDirectoryChangesW(
                dir_handle,
                BUF_LEN,
                True,
                FILE_NOTIFY_CHANGE_FILE_NAME | FILE_NOTIFY_CHANGE_DIR_NAME |
                FILE_NOTIFY_CHANGE_ATTRIBUTES | FILE_NOTIFY_CHANGE_SIZE |
                FILE_NOTIFY_CHANGE_LAST_WRITE | FILE_NOTIFY_CHANGE_SECURITY |
                FILE_NOTIFY_CHANGE_LAST_ACCESS,
                None,
                None
            )

            for action, file_name in results:
                full_path = os.path.join(SYSTEM_DRIVE, file_name)
                print(full_path)
                result = XylentScanner.scanFile(full_path)
                results_queue.put(result)  # Put the result in the queue
                XYLENT_SCAN_CACHE.setVal(full_path, result)

    except KeyboardInterrupt:
        pass
    finally:
        win32file.CloseHandle(dir_handle)
        print("RTP waiting to start...")
