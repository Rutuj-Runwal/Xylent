# Xylent
A powerful antivirus built using Electron framework and python

# ⚠ Work in Progress

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

![Xylent Antivirus StartupMenu Screen](https://github.com/Rutuj-Runwal/Xylent/blob/main/images/Xylent%20StartupMonitorUI.jpg)

### Demo

#### Real Time Protection Demo:

- Carried out with eicar payload
- Instant detection and quarantine of malware


https://github.com/Rutuj-Runwal/Xylent/assets/59436520/61ae2e67-958f-4c75-ba7e-f9554b0438b2

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
