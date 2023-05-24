import { useState, useEffect } from 'react';
import { useLocation } from "react-router-dom";

function ScannerInterface() {
    const [scanReport, setscanReport] = useState([]);
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
        // ----COSMETIC ONLY----
        // setcurrScan("Scanning....");
        // var cosmeticTiming = 500;
        // Object.keys(scanReport).forEach((fileName) => {
        //   if (Object.keys(scanReport).at(-1) == fileName) {
        //     return;
        //   }
        //   cosmeticTiming +=10;
        //   setTimeout(() => { setcurrScan(fileName); }, cosmeticTiming);
        // });
        console.log(scanReport);
        document.getElementsByClassName("loading")[0].style.display = "none";
        if (document.getElementById("scanStats")) {
            document.getElementById("scanStats").style.display = "block";
        }
        document.getElementsByClassName("loading")[0].style.display = "none";
    }

    useEffect(() => {
        Object.keys(scanReport).map((fileName) => {
            if (scanReport[fileName] === "SKIPPED") {
                setskippedFilesCount(skippedFilesCount => skippedFilesCount += 1);
            }
            else if (scanReport[fileName] != "SAFE" && scanReport[fileName] != "CLEAN") {
                setunsafeFilesCount(unsafeFilesCount => unsafeFilesCount += 1);
            }
        })
    }, [scanReport]);

    useEffect(() => {
        runScan();
    }, [])

    // ----COSMETIC ONLY----
    // var nowScanning = () => {
    //   console.log("here");
    //   Object.keys(scanReport).forEach((fileName) => {
    //     if (Object.keys(scanReport).at(-1) == fileName) {
    //       setchecker(1);
    //       return;
    //     }
    //     setTimeout(() => { setcurrScan(fileName); }, 300);
    //   });
    // }

    return (
        <div id="content">
            <h3>Performing {state.scanType} Scan</h3>
            <i className="loading" style={{ display: 'none' }}></i>
            {Object.keys(scanReport).length ?
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