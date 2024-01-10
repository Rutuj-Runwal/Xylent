import os
import ctypes
from parseJson import ParseJson

def scan_and_update(XylentScanner, XYLENT_SCAN_CACHE, pathToScan):
    try:
        # Perform the file scanning operation
        verdict = XylentScanner.scanFile(pathToScan)
        # Update the scan cache with the verdict for the scanned file
        XYLENT_SCAN_CACHE.setVal(pathToScan, verdict)
    except Exception as e:
        # Handle exceptions during the scanning process
        pass  # Sessizce hataları işle, ekrana yazdırma

def systemWatcher(XylentScanner, SYSTEM_DRIVE, thread_resume):
    # Initialize the cache for scanned files
    XYLENT_SCAN_CACHE = ParseJson('./config', 'xylent_scancache', {})
    XYLENT_CACHE_MAXSIZE = 500000  # 500KB

    # Specify the name of the DLL file (e.g., monitor_dll.dll)
    dll_name = "monitor.dll"

    # Specify the full path of the DLL file (in the current folder under the monitordebug folder)
    dll_path = os.path.join(os.getcwd(), "monitordebug", dll_name)

    # Load the DLL
    my_dll = ctypes.CDLL(dll_path)

    # Define the StartMonitoring function
    my_dll.StartMonitoring.argtypes = [ctypes.c_wchar_p]
    my_dll.StartMonitoring.restype = ctypes.c_void_p  # Change the restype to c_void_p

    monitored_path = SYSTEM_DRIVE + "\\"

    # Open a file for writing output
    output_file_path = 'output.txt'
    with open(output_file_path, 'w') as output_file:
        while thread_resume.wait():
            try:
                # Call the StartMonitoring function from the DLL
                output = my_dll.StartMonitoring(monitored_path)

                # Convert the wide string output to a regular Python string
                output_str = ctypes.wstring_at(output).decode("utf-8")

                # Write the output to the file
                output_file.write(output_str + '\n')

                # Call the scanning function
                scan_and_update(XylentScanner, XYLENT_SCAN_CACHE, output_str.strip())
            except Exception as e:
                # Handle exceptions during the scanning process
                pass  # Sessizce hataları işle, ekrana yazdırma

            # Check if the scan cache has exceeded the maximum size
            if os.path.getsize(XYLENT_SCAN_CACHE.PATH) >= XYLENT_CACHE_MAXSIZE:
                # Purge the scan cache if the size exceeds the limit
                XYLENT_SCAN_CACHE.purge()

    # Display a message when the systemWatcher is waiting to start
    print("RTP waiting to start...")

    # Clear the content of the output file after scanning
    with open(output_file_path, 'w') as output_file:
        output_file.write('')
