from parseJson import ParseJson
import subprocess
import threading

def systemWatcher(XylentScanner,thread_resume):
    XYLENT_SCAN_CACHE  = ParseJson('./config', 'xylent_scancache', {})
    process = subprocess.Popen(['monitor.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    def stdout_thread(process):
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"Scanning file: {output.strip()}")  # Print the name of the file being scanned
                verdict = XylentScanner.scanFile(output.strip())
                XYLENT_SCAN_CACHE.setVal(output.strip(), verdict)

    def stderr_thread(process):
        while True:
            error = process.stderr.readline()
            if error == '' and process.poll() is not None:
                break
            if error:
                print(f"Error: {error.strip()}")

    stdout_t = threading.Thread(target=stdout_thread, args=(process,))
    stderr_t = threading.Thread(target=stderr_thread, args=(process,))

    stdout_t.start()
    stderr_t.start()

    stdout_t.join()
    stderr_t.join()
