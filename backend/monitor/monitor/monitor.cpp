#include <windows.h>
#include <tchar.h>
#include <stdio.h>

#ifdef UNICODE
#define tcout wprintf
#else
#define tcout printf
#endif

#define BUF_LEN (10 * (sizeof(FILE_NOTIFY_INFORMATION) + MAX_PATH))

int _tmain(int argc, _TCHAR* argv[]) {
    TCHAR buffer[BUF_LEN];
    DWORD bytes_returned;
    HANDLE dir;

    _TCHAR monitored_path[MAX_PATH] = _T("C:\\");

    dir = CreateFile(
        monitored_path,
        FILE_LIST_DIRECTORY,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        NULL,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS,
        NULL
    );

    if (dir == INVALID_HANDLE_VALUE) {
        tcout(_T("Failed to open directory.\n"));
        return 1;
    }

    while (1) {
        if (!ReadDirectoryChangesW(
            dir,
            buffer,
            BUF_LEN,
            TRUE,
            FILE_NOTIFY_CHANGE_FILE_NAME |
            FILE_NOTIFY_CHANGE_DIR_NAME |
            FILE_NOTIFY_CHANGE_ATTRIBUTES |
            FILE_NOTIFY_CHANGE_SIZE |
            FILE_NOTIFY_CHANGE_LAST_WRITE |
            FILE_NOTIFY_CHANGE_SECURITY |
            FILE_NOTIFY_CHANGE_LAST_ACCESS,
            &bytes_returned,
            NULL,
            NULL
        )) {
            tcout(_T("Failed to read directory changes.\n"));
        }
        else {
            FILE_NOTIFY_INFORMATION* fni = (FILE_NOTIFY_INFORMATION*)buffer;
            _TCHAR full_path[MAX_PATH];
            _tcscpy_s(full_path, monitored_path);

            _tcsncat_s(full_path, fni->FileName, fni->FileNameLength / sizeof(WCHAR));
            tcout(_T("%s\n"), full_path);
        }
    }

    CloseHandle(dir);
    return 0;
}
