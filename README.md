# Xylent
A powerful analysis tool built using Electron framework, Javascript ES6+, python and the flask server framework


### Added Features
- Real Time System Watch
- Database based quering(md5 and sha256)
- Yara based pattern matching analysis
- Executable file signature and integrity analysis
- Quarantine Handler
- Startup Items Management
- Configurable Quick Settings
- Basic Scans -> Quick


### Xylent Interface

![Xylent Antivirus Dashboard](https://raw.githubusercontent.com/Rutuj-Runwal/Xylent/main/images/Xylent%20UI.jpg)

<br/>
<br/>

### Tech Stack:
- Python 
    - Flask 
    - yara
- ElectronJS
- ReactJS
- Webpack/babel

> npm i

> npm run watch

> python engine.py

> npm start

### Architecture
- Flask backend: run using `python engine.py`
- Electron based frontend built on ReactJS 
    - `npm install` to install dependencies 
    - `npm run watch` to compile using webpack 
    - Finally `npm start` to run the app

## Features Demonstration

### Real Time Protection Demo:

- Xylent is capable of detecting and removing Malware
- Blocks drive by downloads
- Prevents malware replication
- Blocks malware on file opening,renaming as well as copying


https://github.com/Rutuj-Runwal/Xylent/assets/59436520/38a76c6f-3bbe-49d7-baa0-c386d96e6492



### Quarantine Management Demo:

- Objects detected are placed into a secure quarantine folder
- Xylent's UI provides a simple interface to restore or safely remove the files


https://github.com/Rutuj-Runwal/Xylent/assets/59436520/86a85662-251d-4d20-a478-055ec5490222



### Archive Auto Repair

- Automatically repair's archive containing malicious files
- Repairs infected files and keeps important data in the archive safe


https://github.com/Rutuj-Runwal/Xylent/assets/59436520/9a5dda8e-2817-4ce4-b570-9799817dc2f8



### Startup monitor Demo:

- Xylent monitors startup items for potential malware
- Currently uses baseline unusual characters and patterns in processname of startup IOC's
- Enable/Disable startup items directly via Xylent's UI


https://github.com/Rutuj-Runwal/Xylent/assets/59436520/99a0af23-0e1e-4f5e-abcc-c7daffc8774f



### Architecture deep-dive

- Xylent consists of a sefver-client based model. The flask(python) based server acts as a "engine" running diagnostics and various analysis such as pattern based matching systems. The client or "the frontend" is a React based application that acts as an interface for the server to relay information. It provides the user with a UI to interact with the server and perform actions with it and also relay notificatons to the user's system based on certain server infromation.
- Scanning and asnalysis occurs on a per file basis where the server checks if a file exists, conveys that info to the client and proceeds with performing static analysis on the given file followed by Yara based pattern matching. In case of a folder or multi file input the engine enumenrates the file in a Unix system order preserving the hierarchy of the folder recursively going through one file at a time.
- Caching: caching is critical for the functioning of Xylent. Along with memory and file size limits set up to ensure smooth operation of the server. Caching stores the verdicts of previous file analysis and uses the cache (if there is no change in file hash MD5/SHA) for subsequent query of the file. This makes scanning faster and reliable. Limits are also setup on type of extensions to scan, the seleciton of file extensions is based on in depth data analaysis of 1000000 samples sorted by thier occurence accounting top 10 most file extension occurence into consideration.

### Expected Features/Coming Soon
- Fuzzy Hashing based detection
- Intelligent/Smart cleaning
    - Cache cleaner -> temp,prefetch, Browser cache...
    - Automatically apply recommended OS settings
- File Insights: [VirusTotal](https://github.com/Rutuj-Runwal/Context-Menu-Scanner) based quering, 
- Web Insights: whois lookup for inbound/outbound urls, virustotal / [McAfee siteadvisor](https://github.com/Rutuj-Runwal/MalwareProtection)
- Basic Scans --> Full,Custom,Memory based scans

### Ambitious/Nice-To-Haves' Features
- Vulnerability Scanner [CVE lookup]
- MITRE ATT&CK report for threats
- In process interruption of malware execution
- [LINUX] ClamAV integration
- File entropy and ML based Heuristic
- AI based malicious pattern detection
- IDS/IPS & HIPS
 
 ### Target Environment
 - Currently in development with main focus towards Windows [both 32-bit and 64x] systems
 - Requires Administrator privilages for certain features
 - Extending capabilites towards Linux at a later stage

### Warranty and License 


    Xylent - A powerful antivirus built using Electron framework and python
    Copyright (C) 2023-present Rutuj Runwal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see {http://www.gnu.org/licenses/}.

    Home: https://github.com/Rutuj-Runwal/Xylent


### Acknowledgements and References
- Use [signature base](https://github.com/Neo23x0/signature-base) by [Florian Roth](https://github.com/Neo23x0) under [Detection Rules license](https://raw.githubusercontent.com/Neo23x0/signature-base/master/LICENSE) for additional detection capabitiies. Place the yare rules in `/backend/signature-base/yara/`
- Custom simple "Dummy" yara rules - [ruleA](https://github.com/Rutuj-Runwal/Xylent/blob/main/backend/signature-base/yara/xylent_test_pdf.yar) & [ruleB](https://github.com/Rutuj-Runwal/Xylent/blob/main/backend/signature-base/yara/xylent_test_word.yar) to detect test malware( of type .docx and .pdf) designed specifically for Xylent Antivirus


