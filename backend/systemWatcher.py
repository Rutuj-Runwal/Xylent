from parseJson import ParseJson
import subprocess

def systemWatcher(XylentScanner, SYSTEM_DRIVE, thread_resume):
    XYLENT_SCAN_CACHE  = ParseJson('./config', 'xylent_scancache', {})
    while thread_resume.wait():
        try:
            # Run monitor.exe and capture the output
            process = subprocess.Popen(['monitor.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            # Ensure the process has completed
            if process.poll() is not None:
                print(stdout.decode('utf-8'))
                print(stderr.decode('utf-8'))

                # Scan each line of the output
                for line in stdout.decode('utf-8').split('\n'):
                    verdict = XylentScanner.scanFile(line.strip())
                    XYLENT_SCAN_CACHE.setVal(line.strip(), verdict)

        except Exception as e:
            print(e)
