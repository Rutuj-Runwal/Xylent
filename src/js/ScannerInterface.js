import { useState, useEffect } from 'react';
import { useLocation } from "react-router-dom";
import { ipcRenderer } from 'electron';
import Store from '../../store';
import { useApiRequest } from './useApiRequest';
function ScannerInterface() {
    const [scanReport, setscanReport] = useState([]);
    const [currScan, setcurrScan] = useState('Scanning');
    const [detectedFiles,setdetectedFiles] = useState([]);
    const [skippedFilesCount, setskippedFilesCount] = useState(0);
    const { state } = useLocation();
    var runScan = async () => {
        // Reset counters
        setskippedFilesCount(0);
        if (document.getElementById("scanStats")) {
            document.getElementById("scanStats").style.display = "none";
        }
        document.getElementsByClassName("loading")[0].style.display = "block";
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scanType: state.scanType })
        };
        var data = await useApiRequest('http://127.0.0.1:5000/initiateScans','POST',{scanType:state.scanType},'json')
        setscanReport(data);

        document.getElementsByClassName("loading")[0].style.display = "none";
        if (document.getElementById("scanStats")) {
            document.getElementById("scanStats").style.display = "block";
        }
        document.getElementsByClassName("loading")[0].style.display = "none";
        console.log(data);
        return data;
    }
    var setQuar = (id,detection) => {
        console.log("Contained threat: " + id);
        useApiRequest('http://127.0.0.1:5000/quarFile', 'POST', {originalPath: id, detectionSpace: detection})
        .then(data => console.log(data))
        .then(() => setdetectedFiles(detectedFiles.filter(item => item[0]!=id)));
    }

    useEffect(() => {
        // ----COSMETIC ONLY----
        let indx = 0 , interval;
        interval = setInterval(() => {
            if (Object.keys(scanReport)[indx] == Object.keys(scanReport)[Object.keys(scanReport).length - 1]) {
                setcurrScan("scanning animation done");
                clearInterval(interval);
            }
            else{
                setcurrScan(Object.keys(scanReport)[indx])
                indx++;
            }
        }, 200);
        let unsafeItem = [];
        Object.keys(scanReport).map((fileName) => {
            if (scanReport[fileName] === "SKIPPED") {
                setskippedFilesCount(skippedFilesCount => skippedFilesCount += 1);
            }
            else if (scanReport[fileName] != "SAFE") {
                unsafeItem.push([fileName,scanReport[fileName]]);
            }
        })
        setdetectedFiles(unsafeItem);
        
        // Save dashboard statistics
        ipcRenderer.send('xylent-get-path', "XYLENT_GET_APP_PATH");
        ipcRenderer.once('xylent-get-path', (event, basePath) => {
            const store = new Store({
                configName: "system_stats",
                defaults: {
                    "Threats Blocked": 0,
                    "Items Scanned":0
                },
                userPath: basePath + "/config/"
            })
            store.set('Threats Blocked', store.get('Threats Blocked') + unsafeItem.length);
            store.set('Items Scanned', store.get('Items Scanned') + Object.keys(scanReport).length);
        });
        return () => {
            clearInterval(interval);
        }
    }, [scanReport]);

    useEffect(() => {
        runScan();
    }, [])

    return (
        <div>
            <h3>Performing {state.scanType} Scan</h3>
            <i className="loading" style={{ display: 'none' }}></i>
            {currScan != "scanning animation done" ? currScan : 
                Object.keys(scanReport).length ?
                    <div id="scanStats">
                        <span>Total Files Analyzed: {Object.keys(scanReport).length}</span>
                        <br />
                        <span>Files Skipped: {skippedFilesCount}</span>
                        <br />
                        <span>Malware Detected: {detectedFiles.length}</span>
                        <br/><br/>
                        <div>
                            <table>
                                <tbody>
                                {detectedFiles.map((fileData) => {
                                    return(
                                        <tr key={fileData[0]}>
                                            <td>{fileData[0]}</td>
                                            <td>{fileData[1]}</td>
                                            <td><button id={fileData[0]} className='itemStatusPill' style={{ 'backgroundColor': "lightgreen" }} onClick={(e) => setQuar(e.target.id,fileData[1])}>Quarantine</button></td>
                                            <td><button id={fileData[0]} className='itemStatusPill' style={{ 'backgroundColor': 'lightred' }}>Ignore</button></td>
                                        </tr>
                                    )
                                })}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    : <></>
            }
        </div>
    )
}

export default ScannerInterface