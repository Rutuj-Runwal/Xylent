// main.cpp
#include <windows.h>
#include <tchar.h>
#include <stdio.h>
#include <cstdlib>

void StartMonitoring(const TCHAR* monitoredPath);

int _tmain(int argc, _TCHAR* argv[])
{
    // Monitor "C:\\" directory
    StartMonitoring(_T("C:\\"));

    return 0;
}

void StartMonitoring(const TCHAR* monitoredPath)
{
    DWORD buffer_size = 10 * (sizeof(FILE_NOTIFY_INFORMATION) + MAX_PATH);
    TCHAR* buffer = (TCHAR*)malloc(buffer_size);

    if (buffer == NULL) {
        // Handle memory allocation failure
        return;
    }

    DWORD bytes_returned;
    HANDLE dir;

    dir = CreateFile(
        monitoredPath,
        FILE_LIST_DIRECTORY,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        NULL,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS,
        NULL
    );

    if (dir == INVALID_HANDLE_VALUE) {
        _ftprintf(stderr, _T("Failed to open directory.\n"));
        free(buffer);
        return;
    }

    while (1) {
        if (!ReadDirectoryChangesW(
            dir,
            buffer,
            buffer_size,
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
            _ftprintf(stderr, _T("Failed to read directory changes.\n"));
        }
        else {
            FILE_NOTIFY_INFORMATION* fni = (FILE_NOTIFY_INFORMATION*)buffer;
            _TCHAR full_path[MAX_PATH];
            _tcscpy_s(full_path, monitoredPath);

            _TCHAR filename[MAX_PATH];
            _tcsncpy_s(filename, fni->FileName, fni->FileNameLength / sizeof(WCHAR));
            filename[fni->FileNameLength / sizeof(WCHAR)] = '\0'; // Add null terminator

            if (full_path[_tcslen(full_path) - 1] != '\\') {
                _tcscat_s(full_path, _T("\\"));
            }

            _tcscat_s(full_path, filename);

            FILE* file;
            if (_tfopen_s(&file, _T("output.txt"), _T("a")) == 0) {
                _ftprintf(file, _T("%s\n"), full_path);
                fclose(file);
            }
        }
    }

    CloseHandle(dir);
    free(buffer);
}
