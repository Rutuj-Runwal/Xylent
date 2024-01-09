import ctypes
import os
import win32file
import win32con
from queue import Queue
import concurrent.futures
import threading
from parseJson import ParseJson

FILE_ACTION_ADDED = 0x00000001
FILE_ACTION_REMOVED = 0x00000002
FILE_ACTION_MODIFIED = 0x00000003
FILE_NOTIFY_CHANGE_LAST_ACCESS = 0x00000020
FILE_LIST_DIRECTORY = 0x0001

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
                win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE |
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
                FILE_NOTIFY_CHANGE_LAST_ACCESS |
                FILE_ACTION_ADDED |
                FILE_ACTION_MODIFIED |
                FILE_ACTION_REMOVED,
                None,
                None
            )

            for action, file in results:
                path_to_scan = os.path.join(path_to_watch, file)
                print(path_to_scan)  # Print the path for debugging purposes
                result3 = XylentScanner.scanFile(path_to_scan)
                results_queue.put(result3)  # Put the result in the queue
                XYLENT_SCAN_CACHE.setVal(path_to_scan, result3)

    def watch_processes():
        global printed_processes
        global previous_list

        # Print the initially running processes
        initial_processes = get_running_processes()
        print("Initially running processes:")
        print(initial_processes)

        printed_processes = set()

        # Load new processes using ParseJson
        new_processes = load_new_processes()

        # Initialize previous_list
        previous_list = initial_processes

        while thread_resume.is_set():
            try:
                # Get current running processes
                current_list = get_running_processes()

                # Compare with the previous list and find new processes
                newly_started_processes = current_list - previous_list
                new_processes.update(dict.fromkeys(newly_started_processes))

                if newly_started_processes:
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        # Submit each task individually and pass the required arguments
                        futures = [executor.submit(new_process_checker, info, XylentScanner, results_queue) for info in newly_started_processes]
                        concurrent.futures.wait(futures)

                    # Print new processes once
                    print("Newly started processes:")
                    print(newly_started_processes)

                    # Update printed_processes to avoid printing the same processes again
                    printed_processes.update(newly_started_processes)

                # Update the previous list
                previous_list = current_list

                # Save the updated new processes list to the file using ParseJson
                save_new_processes(list(new_processes))
            except Exception as e:
                print(f"Error in watch_processes: {e}")

    def load_new_processes():
        try:
            return XYLENT_NEW_PROCESS_INFO.parseDataFile([])
        except Exception:
            return []

    def save_new_processes(new_processes):
        XYLENT_NEW_PROCESS_INFO.setVal("new_processes", new_processes)

    def get_running_processes():
        processes = set()
        # Enumerate all processes
        for pid in range(1, 32767):  # Maximum possible PID on Windows is 32767
            exe_path = get_process_info(pid)
            if exe_path:
                cmdline = get_cmdline(pid)
                ppid = get_parent_pid(pid)
                processes.add((exe_path, cmdline, ppid))
        return processes

    def get_process_info(pid):
        try:
            process_handle = ctypes.windll.kernel32.OpenProcess(0x0400 | 0x0010, False, pid)
            if process_handle:
                # Get process information
                buffer_size = 1000
                buffer = ctypes.create_unicode_buffer(buffer_size)
                ctypes.windll.kernel32.QueryFullProcessImageNameW(process_handle, 0, buffer, ctypes.byref(buffer_size))
                exe_path = buffer.value

                return exe_path

        except Exception as e:
            print(f"Error getting process info: {e}")

        finally:
            if process_handle:
                ctypes.windll.kernel32.CloseHandle(process_handle)

        return None

    def get_cmdline(pid):
        try:
            process_handle = ctypes.windll.kernel32.OpenProcess(0x0400 | 0x0010, False, pid)
            if process_handle:
                # Get command line
                buffer_size = 1000
                buffer = ctypes.create_unicode_buffer(buffer_size)
                ctypes.windll.kernel32.GetModuleFileNameExW(process_handle, 0, buffer, buffer_size)
                cmdline = buffer.value

                return cmdline

        except Exception as e:
            print(f"Error getting cmdline: {e}")

        finally:
            if process_handle:
                ctypes.windll.kernel32.CloseHandle(process_handle)

        return None

    def get_parent_pid(pid):
        try:
            process_handle = ctypes.windll.kernel32.OpenProcess(0x0400 | 0x0010, False, pid)
            if process_handle:
                ppid_buffer = ctypes.c_ulong()
                ctypes.windll.kernel32.GetWindowThreadProcessId(ctypes.windll.user32.GetShellWindow(), ctypes.byref(ppid_buffer))
                parent_pid = ppid_buffer.value

                return parent_pid

        except Exception as e:
            print(f"Error getting parent pid: {e}")

        finally:
            if process_handle:
                ctypes.windll.kernel32.CloseHandle(process_handle)

        return None

    def new_process_checker(process_info, XylentScanner, results_queue):
        global printed_processes

        # process_info is a tuple (exe, cmdline, pid)
        exe, cmdline, pid = process_info

        if exe not in printed_processes:
            # Print the running file only once
            print(f"Running File: {exe}")
            printed_processes.add(exe)

            parent_path = get_process_info(get_parent_pid(pid))

            # Check if parent and child have the same location
            if parent_path != "Unknown" and exe.startswith(parent_path):
                return  # Skip processing if they have the same location

            # Check if parent and child have the same full path
            if os.path.abspath(exe) == os.path.abspath(parent_path):
                return  # Skip processing if they have the same full path

            message = f"Path: {exe}, Parent Process Path: {parent_path}, Command Line: {cmdline}"
                    # Include the running file itself in the path_to_scan
            result2 = XylentScanner.scanFile(exe)
            results_queue.put(result2)  # Put the result in the queue
            XYLENT_SCAN_CACHE.setVal(exe,result2)
            result3 = XylentScanner.scanFile(parent_path)
            results_queue.put(result3)  # Put the result in the queue
            XYLENT_SCAN_CACHE.setVal(parent_path,result3)
            # Print to the console
            print("New Process Detected:", message)

            # Check if the command line includes paths
            if isinstance(cmdline, list):  # Ensure cmdline is a list
                paths = [arg for arg in cmdline if os.path.isabs(arg) and os.path.exists(arg)]
                if paths:
                    print(f"Command Line includes paths: {paths}, scanning related folder for process {exe}")
                    # Assuming you have a method named 'scanFile' in your Scanner class
                    for path in paths:
                        result = XylentScanner.scanFile(path)
                        results_queue.put(result)  # Put the result in the queue
                        XYLENT_SCAN_CACHE.setVal(path,result)
    
    # Create a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks to the executor
        monitor_thread_future = executor.submit(file_monitor)
        watch_processes_thread_future = executor.submit(watch_processes)

        # Wait for all tasks to complete
        concurrent.futures.wait([monitor_thread_future, watch_processes_thread_future])

    print("RTP waiting to start...")
