from queue import Queue
from parseJson import ParseJson
import ctypes 

FILE_NOTIFY_CHANGE_FILE_NAME = 0x00000001
FILE_NOTIFY_CHANGE_DIR_NAME = 0x00000002
FILE_NOTIFY_CHANGE_ATTRIBUTES = 0x00000004
FILE_NOTIFY_CHANGE_SIZE = 0x00000008
FILE_NOTIFY_CHANGE_LAST_WRITE = 0x00000010
FILE_NOTIFY_CHANGE_SECURITY = 0x00000100
FILE_NOTIFY_CHANGE_LAST_ACCESS = 0x00000020

BUF_LEN = 10 * (16 + 260)  # Size of FILE_NOTIFY_INFORMATION structure (16) + Maximum Path Length (260)

# Hexadecimal
OPEN_EXISTING = 0x00000003
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_SHARE_DELETE = 0x00000004
FILE_LIST_DIRECTORY = 0x0001

# Initialize ParseJson
XYLENT_NEW_PROCESS_INFO = ParseJson('./config', 'new_processes.json', {})

# Add global declarations for 'printed_processes' and 'previous_list'
printed_processes = set()
previous_list = set()
results_queue = Queue()  # Define results_queue as a global variable

# Structure definition
class FILE_NOTIFY_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("NextEntryOffset", ctypes.c_ulong),
        ("Action", ctypes.c_ulong),
        ("FileNameLength", ctypes.c_ulong),
        ("FileName", ctypes.c_wchar * 1)  # Variable length, adjusted in code
    ]

# Function to replace ctypes.windll.kernel32
def CreateFileW(lpFileName, dwDesiredAccess, dwShareMode, lpSecurityAttributes, dwCreationDisposition, dwFlagsAndAttributes, hTemplateFile):
    return ctypes.windll.kernel32.CreateFileW(
        lpFileName,
        dwDesiredAccess,
        dwShareMode,
        lpSecurityAttributes,
        dwCreationDisposition,
        dwFlagsAndAttributes,
        hTemplateFile
    )

def CloseHandle(hObject):
    return ctypes.windll.kernel32.CloseHandle(hObject)

def ReadDirectoryChangesW(hDirectory, lpBuffer, nBufferLength, bWatchSubtree, dwNotifyFilter, lpBytesReturned, lpOverlapped, lpCompletionRoutine):
    return ctypes.windll.kernel32.ReadDirectoryChangesW(
        hDirectory,
        lpBuffer,
        nBufferLength,
        bWatchSubtree,
        dwNotifyFilter,
        lpBytesReturned,
        lpOverlapped,
        lpCompletionRoutine
    )

def systemWatcher(XylentScanner, SYSTEM_DRIVE, thread_resume):
    XYLENT_SCAN_CACHE = ParseJson('./config', 'xylent_scancache', '')
    
    monitored_path = SYSTEM_DRIVE + "\\"

    # Initialize buffer with enough space for FILE_NOTIFY_INFORMATION structure
    buffer = (ctypes.c_ubyte * BUF_LEN)()

    bytes_returned = ctypes.c_ulong()
    dir_handle = ctypes.c_void_p()

    dir_handle = CreateFileW(
        monitored_path,
        FILE_LIST_DIRECTORY,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        None,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS,
        None
    )

    if dir_handle.value == -1:
        print("Failed to open directory.")
        return

    try:
        while thread_resume.is_set():
            if not ReadDirectoryChangesW(
                dir_handle,
                buffer,
                BUF_LEN,
                True,
                FILE_NOTIFY_CHANGE_FILE_NAME | FILE_NOTIFY_CHANGE_DIR_NAME | FILE_NOTIFY_CHANGE_ATTRIBUTES | FILE_NOTIFY_CHANGE_SIZE | FILE_NOTIFY_CHANGE_LAST_WRITE | FILE_NOTIFY_CHANGE_SECURITY | FILE_NOTIFY_CHANGE_LAST_ACCESS,
                ctypes.byref(bytes_returned),
                None,
                None
            ):
                print("Failed to read directory changes.")
            else:
                # Access the FILE_NOTIFY_INFORMATION structure using raw buffer
                fni = FILE_NOTIFY_INFORMATION.from_buffer(buffer)

                # Build full path by joining the monitored path and the file name
                full_path = monitored_path + "\\" + fni.FileName

                print(full_path)  # Debug için yazıldı

                # Perform the required operations on the scanned file
                result = XylentScanner.scanFile(full_path)

                # Put the result in the queue
                results_queue.put(result)

                # Update the Xylent scan cache
                XYLENT_SCAN_CACHE.setVal(full_path, result)

    except KeyboardInterrupt:
        pass
    finally:
        CloseHandle(dir_handle)
        print("RTP waiting to start...")
