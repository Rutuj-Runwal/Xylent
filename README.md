# Xylent
A powerful antivirus built using Electron framework and python


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
 
 ### Target Environment
 - Currently in development with main focus towards Windows [both 32-bit and 64x] systems
 - Requires Administrator privilages for certain features
 - Extending capabilites towards Linux at a later stage

### Acknowledgements and References
- Use [signature base](https://github.com/Neo23x0/signature-base) by [Florian Roth](https://github.com/Neo23x0) under [Detection Rules license](https://raw.githubusercontent.com/Neo23x0/signature-base/master/LICENSE) for additional detection capabitiies. Place the yare rules in `/backend/signature-base/yara/`
- Custom simple "Dummy" yara rules - [ruleA](https://github.com/Rutuj-Runwal/Xylent/blob/main/backend/signature-base/yara/xylent_test_pdf.yar) & [ruleB](https://github.com/Rutuj-Runwal/Xylent/blob/main/backend/signature-base/yara/xylent_test_word.yar) to detect test malware( of type .docx and .pdf) designed specifically for Xylent Antivirus
