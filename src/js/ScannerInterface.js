import { useState, useEffect } from 'react';
import { useLocation } from "react-router-dom";

function ScannerInterface() {
    const [scanReport, setscanReport] = useState([]);
    const [currScan, setcurrScan] = useState('Scanning')
    const [skippedFilesCount, setskippedFilesCount] = useState(0);
    const [unsafeFilesCount, setunsafeFilesCount] = useState(0);
    const { state } = useLocation();
    var runScan = async () => {
        // Reset counters
        setskippedFilesCount(0);
        setunsafeFilesCount(0);
        if (document.getElementById("scanStats")) {
            document.getElementById("scanStats").style.display = "none";
        }
        document.getElementsByClassName("loading")[0].style.display = "block";
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scanType: state.scanType })
        };
        var data = await fetch('http://127.0.0.1:5000/initiateScans', requestOptions)
        var dataJ = await data.json();
        setscanReport(dataJ);

        document.getElementsByClassName("loading")[0].style.display = "none";
        if (document.getElementById("scanStats")) {
            document.getElementById("scanStats").style.display = "block";
        }
        document.getElementsByClassName("loading")[0].style.display = "none";
        console.log(dataJ);
        return dataJ;
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
        Object.keys(scanReport).map((fileName) => {
            if (scanReport[fileName] === "SKIPPED") {
                setskippedFilesCount(skippedFilesCount => skippedFilesCount += 1);
            }
            else if (scanReport[fileName] != "SAFE") {
                setunsafeFilesCount(unsafeFilesCount => unsafeFilesCount += 1);
            }
        }) 
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
                        <span>Malware Detected: {unsafeFilesCount}</span>
                    </div>
                    : <></>
            }
        </div>
    )
}

export default ScannerInterface