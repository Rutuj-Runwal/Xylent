import os
import win32file
import win32con
from queue import Queue
from parseJson import ParseJson
import psutil
import concurrent.futures

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
    while thread_resume.is_set():
        def file_monitor():
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
                        full_path = os.path.abspath(full_path)  # Ensure the full path is absolute
                        result = XylentScanner.scanFile(full_path)
                        results_queue.put((full_path, result))  # Put the result and path in the queue
                        XYLENT_SCAN_CACHE.setVal(full_path, result)
                        print(full_path)  # Print the path here

            except KeyboardInterrupt:
                pass
            finally:
                win32file.CloseHandle(dir_handle)

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
            for p in psutil.process_iter(['exe', 'cmdline', 'ppid']):
                try:
                    if p.info is not None and 'exe' in p.info:
                        exe = p.info['exe']
                        cmdline = tuple(p.info.get('cmdline', []))
                        ppid = p.info.get('ppid', None)
                        processes.add((exe, cmdline, ppid))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, TypeError):
                    pass  # Skip processes that are inaccessible or no longer exist
                except Exception as e:
                    print(f"Error getting process info: {e}")
            return processes

        def new_process_checker(process_info, XylentScanner, results_queue):
            global printed_processes

            # process_info is a tuple (exe, cmdline, pid)
            exe, cmdline, pid = process_info

            if exe not in printed_processes:
                # Print the running file only once
                print(f"Running File: {exe}")
                printed_processes.add(exe)
                result0 = XylentScanner.scanFile(exe)
                results_queue.put(result0)  # Put the result in the queue
                parent_process_info = get_parent_process_info(pid)
                if parent_process_info is None or parent_process_info.get('exe') is None:
                    return  # Skip processing if parent process info is None or has no executable information

                parent_path = parent_process_info['exe']

                # Check if parent and child have the same location
                if parent_path != "Unknown" and exe.startswith(parent_path):
                    return  # Skip processing if they have the same location

                # Check if parent and child have the same full path
                if os.path.abspath(exe) == os.path.abspath(parent_path):
                    return  # Skip processing if they have the same full path

                message = f"Path: {exe}, Parent Process Path: {parent_path}, Command Line: {cmdline}"
                result = XylentScanner.scanFile(parent_path)
                results_queue.put(result)  # Put the result in the queue
                # Print to the console
                print("New Process Detected:", message)

                # Check if the command line includes paths
                if isinstance(cmdline, list):  # Ensure cmdline is a list
                    paths = [arg for arg in cmdline if os.path.isabs(arg) and os.path.exists(arg)]
                    if paths:
                        print(f"Command Line includes paths: {paths}, scanning related folder for process {exe}")
                        # Assuming you have a method named 'scanFile' in your Scanner class
                        for path in paths:
                            result1 = XylentScanner.scanFile(path)
                            results_queue.put(result1)  # Put the result in the queue

        def get_parent_process_info(file_path):
            try:
                process = psutil.Process(os.getpid())
                for parent in process.parents():
                    if parent.exe() == file_path:
                        return {
                            'name': parent.name(),
                            'exe': parent.exe(),
                            'cmdline': parent.cmdline(),
                            'pid': parent.pid,
                        }
                return None
            except psutil.NoSuchProcess:
                print(f"Error: No such process with path {file_path}")
            except psutil.AccessDenied:
                print(f"Error: Access denied while retrieving information for path {file_path}")
            except Exception as e:
                print(f"An unexpected error occurred while getting parent process info for path {file_path}: {e}")

            return None

        # Create a ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit tasks to the executor
            monitor_thread_future = executor.submit(file_monitor)
            watch_processes_thread_future = executor.submit(watch_processes)

        # Wait for all tasks to complete
        concurrent.futures.wait([monitor_thread_future, watch_processes_thread_future])

    print("RTP waiting to start...")
