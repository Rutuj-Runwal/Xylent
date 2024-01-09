import os
import ctypes
from parseJson import ParseJson

def systemWatcher(XylentScanner, SYSTEM_DRIVE, thread_resume, pathToScan):
    XYLENT_SCAN_CACHE = ParseJson('./config', 'xylent_scancache', {})
    XYLENT_CACHE_MAXSIZE = 500000  # 500KB

    # DLL dosyasının adını belirtin (örneğin, monitor_dll.dll)
    dll_name = "monitor.dll"

    # DLL dosyasının tam yolu (mevcut klasördeki monitor klasöründe)
    dll_path = os.path.join(os.getcwd(), "monitordebug", dll_name)

    # DLL'i yükle
    my_dll = ctypes.CDLL(dll_path)

    # StartMonitoring fonksiyonunu çağır
    monitored_path = SYSTEM_DRIVE
    my_dll.StartMonitoring.argtypes = [ctypes.c_wchar_p]
    my_dll.StartMonitoring.restype = None
    my_dll.StartMonitoring(monitored_path)

    while thread_resume.wait():
        try:
            if pathToScan:
                verdict = XylentScanner.scanFile(pathToScan)
                XYLENT_SCAN_CACHE.setVal(pathToScan, verdict)
        except Exception as e:
            print(e)

        if os.path.getsize(XYLENT_SCAN_CACHE.PATH) >= XYLENT_CACHE_MAXSIZE:
            XYLENT_SCAN_CACHE.purge()
            print("Purging")

    print("RTP waiting to start...")
