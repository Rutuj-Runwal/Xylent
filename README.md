# Xylent
A powerful antivirus built using Electron framework and python

⚠ Work in Progress

### Expected Features
- Real Time System Watch
- File Insights: [VirusTotal](https://github.com/Rutuj-Runwal/Context-Menu-Scanner) based quering, 
- Web Insights: whois lookup for inbound/outbound urls, virustotal / [McAfee siteadvisor](https://github.com/Rutuj-Runwal/MalwareProtection)
- Database based quering(md5 and sha256)
- Yara based pattern matching analysis
- AI based flow detector/Heuristic
- Basic Scans -> Quick,Full,Custom
- Intelligent/Smart cleaning
    - Cache cleaner -> temp,prefetch, Browser cache...
    - Disable/Enable startup 

### Ambitious/Nice-To-Haves' Features
- Vulnerability Scanner [CVE lookup]
- MITRE ATT&CK analysis
- In process interruption of malware execution

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
