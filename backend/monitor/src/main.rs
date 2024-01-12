extern crate winapi;

use std::ffi::OsStr;
use std::iter::once;
use std::os::windows::ffi::OsStrExt;
use std::ptr::null_mut;
use std::fs::File;
use std::io::Write;
use std::slice;
use winapi::um::winnt::HANDLE;
use winapi::um::winbase::{ReadDirectoryChangesW, FILE_FLAG_BACKUP_SEMANTICS};
use winapi::um::fileapi::{CreateFileW, OPEN_EXISTING};
use winapi::um::winnt::{FILE_LIST_DIRECTORY, FILE_SHARE_READ, FILE_SHARE_WRITE, FILE_NOTIFY_INFORMATION, FILE_NOTIFY_CHANGE_LAST_ACCESS, FILE_NOTIFY_CHANGE_FILE_NAME, FILE_NOTIFY_CHANGE_DIR_NAME, FILE_NOTIFY_CHANGE_ATTRIBUTES, FILE_NOTIFY_CHANGE_SIZE, FILE_NOTIFY_CHANGE_LAST_WRITE, FILE_NOTIFY_CHANGE_SECURITY};

fn main() {
    let path = OsStr::new("C:\\")
        .encode_wide()
        .chain(once(0))
        .collect::<Vec<_>>();

    unsafe {
        let handle: HANDLE = CreateFileW(
            path.as_ptr(),
            FILE_LIST_DIRECTORY,
            FILE_SHARE_READ | FILE_SHARE_WRITE,
            null_mut(),
            OPEN_EXISTING,
            FILE_FLAG_BACKUP_SEMANTICS,
            null_mut(),
        );

        let mut buffer = [0u8; 1024];
        let mut bytes_returned = 0u32;
        let mut output_file = File::create("output.txt").unwrap();

        loop {
            let result = ReadDirectoryChangesW(
                handle,
                buffer.as_mut_ptr() as *mut _,
                buffer.len() as u32,
                1,
                FILE_NOTIFY_CHANGE_FILE_NAME |
                FILE_NOTIFY_CHANGE_DIR_NAME |
                FILE_NOTIFY_CHANGE_ATTRIBUTES |
                FILE_NOTIFY_CHANGE_SIZE |
                FILE_NOTIFY_CHANGE_LAST_WRITE |
                FILE_NOTIFY_CHANGE_SECURITY |
                FILE_NOTIFY_CHANGE_LAST_ACCESS,
                &mut bytes_returned,
                null_mut(),
                None,
            );

            if result == 0 {
                eprintln!("Failed to read directory changes.");
                break;
            }

            let info = &*(buffer.as_ptr() as *const FILE_NOTIFY_INFORMATION);
            let filename = slice::from_raw_parts(info.FileName.as_ptr(), info.FileNameLength as usize / 2);
            let filename = String::from_utf16_lossy(filename);
            writeln!(output_file, "C:\\{}", filename).unwrap();
        }
    }
}