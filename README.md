# Xylent
A powerful antivirus built using Electron framework and python

### Expected Features

- Real Time System Watch
- File Insights: Virustotal based quering, 
- Web Insights: whois lookup for inbound/outbound urls, virustotal/Mcafee siteadvisor
- Database based quering(md5 and sha256)
- AI based flow detector/Heuristic
- Basic Scans -> Quick,Full,Custom
- Intelligent/Smart cleaning
    - Cache cleaner -> temp,prefetch, Browser cache...
    - Disable/Enable startup 

### Tech Stack:
- Python - 
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