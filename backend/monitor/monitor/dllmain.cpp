// dllmain.cpp
#include "pch.h"

BOOL APIENTRY DllMain(HMODULE hModule,
    DWORD  ul_reason_for_call,
    LPVOID lpReserved
)
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}

#include <windows.h>
#include <tchar.h>
#include <stdio.h>
#include <cstdlib>

extern "C" __declspec(dllexport) void StartMonitoring(const TCHAR* monitoredPath)
{
    DWORD buffer_size = 10 * (sizeof(FILE_NOTIFY_INFORMATION) + MAX_PATH);
    TCHAR* buffer = (TCHAR*)malloc(buffer_size);

    if (buffer == NULL) {
        // Handle memory allocation failure
        return;
    }

    HANDLE dir = CreateFile(
        monitoredPath,
        FILE_LIST_DIRECTORY,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        NULL,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS,
        NULL
    );

    if (dir == INVALID_HANDLE_VALUE) {
        FILE* file;
        if (_wfopen_s(&file, L"output.txt", L"a") == 0) {
            _ftprintf(file, _T("Failed to open directory.\n"));
            fclose(file);
        }
        free(buffer);
        return;
    }

    FILE* file;
    if (_wfopen_s(&file, L"output.txt", L"a") != 0) {
        // Handle file opening failure
        free(buffer);
        CloseHandle(dir);
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
            NULL,
            NULL,
            NULL
        )) {
            // Handle ReadDirectoryChangesW failure
            _ftprintf(file, _T("Failed to read directory changes.\n"));
        }
        else {
            FILE_NOTIFY_INFORMATION* fni = (FILE_NOTIFY_INFORMATION*)buffer;
            TCHAR full_path[MAX_PATH];

            // Ensure proper null-termination
            full_path[0] = _T('\0');

            // Copy monitoredPath to full_path
            _tcsncpy_s(full_path, MAX_PATH, monitoredPath, MAX_PATH - _tcslen(fni->FileName) - 1);

            // Concatenate the filename to full_path
            _tcsncat_s(full_path, MAX_PATH, fni->FileName, fni->FileNameLength / sizeof(WCHAR));

            // Print to console
            _tprintf(_T("%s\n"), full_path);

            // Output to file
            _ftprintf(file, _T("%s\n"), full_path);

            // Release the file handle to allow other programs to read
            CloseHandle(dir);
            // Reopen the directory to continue monitoring
            dir = CreateFile(
                monitoredPath,
                FILE_LIST_DIRECTORY,
                FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                NULL,
                OPEN_EXISTING,
                FILE_FLAG_BACKUP_SEMANTICS,
                NULL
            );

            // Handle directory reopening failure
            if (dir == INVALID_HANDLE_VALUE) {
                _ftprintf(file, _T("Failed to reopen directory for monitoring.\n"));
                break;  // Exit the loop if reopening fails
            }
        }
    }

    // Close the file handle after the loop
    fclose(file);
    CloseHandle(dir);
    free(buffer);
}
