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
        // Handle directory open failure
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
            NULL,
            NULL,
            NULL
        )) {
            // Handle ReadDirectoryChangesW failure
        }
        else {
            FILE_NOTIFY_INFORMATION* fni = (FILE_NOTIFY_INFORMATION*)buffer;
            TCHAR full_path[MAX_PATH];

            _tcscpy_s(full_path, monitoredPath);
            _tcscat_s(full_path, _T("\\"));
            _tcsncat_s(full_path, MAX_PATH, fni->FileName, fni->FileNameLength / sizeof(TCHAR));

            _tprintf(_T("%s\n"), full_path);

            FILE* file;
            if (_wfopen_s(&file, L"output.txt", L"a") == 0) {
                _ftprintf(file, _T("%s\n"), full_path);
                fclose(file);
            }

            CloseHandle(dir);
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
                break;
            }
        }
    }

    CloseHandle(dir);
    free(buffer);
}
