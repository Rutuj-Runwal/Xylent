import { useState } from 'react';
import { useNavigate } from "react-router-dom";
function Status() {
  const [skippedFilesCount, setskippedFilesCount] = useState(0);
  let navigate = useNavigate();
  const routeChange = () => {
    let path = `/scanUI`;
    navigate(path, { state: { scanType: "Quick" } });
  }
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
    <div id="homeContent">
      <h3 style={{ "textAlign": 'center' }}>Welcome to Xylent Antivirus!</h3>
      <div className="flex_row just_cent">
        <div>
          <div className="circle">
            <div className="checkMark"></div>
          </div>
        </div>
        <div className='flex_col just_cent'>
          <p style={{ 'fontSize': '30px' }}>&nbsp;&nbsp;&nbsp;System is Secure</p>
          <button onClick={routeChange} id="homeScanNow_Btn">Scan Now</button>
        </div>
      </div>
      <br />
      <div className='flex_row'>
        <div className='statBox flex_col'>
          <div className='statBox_head flex_row spc_btwn'>
            <div>{skippedFilesCount}</div>
            <div>Placeholder</div>
          </div>
          <div>Malware/Viruses</div>
        </div>
        <div className='statBox flex_col'>
          <div className='statBox_head flex_row spc_btwn'>
            <div>{skippedFilesCount}</div>
            <div>Placeholder</div>
          </div>
          <div>Malware/Viruses</div>
        </div>
        <div className='statBox flex_col'>
          <div className='statBox_head flex_row spc_btwn'>
            <div>{skippedFilesCount}</div>
            <div>Placeholder</div>
          </div>
          <div>Malware/Viruses</div>
        </div>
      </div>
      {/* <h2 id="nowScanning">{currScan}</h2> */}
    </div>
  )
}

export default Status