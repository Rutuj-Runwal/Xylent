import os
import win32file
import win32con
import time
def systemWatcher(XylentScanner,SYSTEM_DRIVE,thread_resume):
  while thread_resume.wait():
    path_to_watch = SYSTEM_DRIVE+"\\"
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
      pathToScan = os.path.join(path_to_watch, file)
      print(pathToScan)
      if SYSTEM_DRIVE + "\\Windows\\Prefetch\\" in pathToScan:
        pathToScan = ""
      elif SYSTEM_DRIVE + "\\Windows\\Temp" in pathToScan:
        pathToScan = ""
      elif SYSTEM_DRIVE + "\\$Recycle.Bin" in pathToScan:
        pathToScan = ""
      elif SYSTEM_DRIVE + "\\Windows\\ServiceState" in pathToScan:
        pathToScan = ""
      elif SYSTEM_DRIVE + "\\Windows\\Logs" in pathToScan:
        pathToScan = ""
      elif SYSTEM_DRIVE + "\\Windows\\ServiceProfiles" in pathToScan:
        pathToScan = ""
      elif SYSTEM_DRIVE + "\\Windows\\System32" in pathToScan:
        pathToScan = ""
      elif SYSTEM_DRIVE + "\\Windows\\bootstat.dat" in pathToScan:
        pathToScan = ""
      elif XylentScanner.quar.QuarantineDir in pathToScan:
        pathToScan = ""
      try:
          if pathToScan:
            XylentScanner.scanFile(pathToScan)
      except Exception as e:
        print(e)
        print(str(action)+" "+file+" ")

  print("RTP waiting to start...")
