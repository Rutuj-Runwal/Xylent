import { useEffect } from 'react';
import { useNavigate,Link } from "react-router-dom";
import { LuTrash } from "react-icons/lu";
import { TbHeartRateMonitor } from "react-icons/tb";
import { RiScanLine } from "react-icons/ri";
import { ipcRenderer } from 'electron';
import Store from '../../store';
function Status() {
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
  useEffect(() => {
    ipcRenderer.send('xylent-get-path', "XYLENT_GET_APP_PATH");
    ipcRenderer.once('xylent-get-path', (event, basePath) => {
      const store = new Store({
        configName: "user_preference",
        defaults: {
          "Real Time Protection": true,
          "Notification": false,
          "Notification Duration": 2,
          "Auto check for definition updates": true,
          "Auto check for program updates": true,
          "Scan PE files": true,
          "Apply additional checks for archives": true,
          "Treat un-signed executables as suspicious": true,
          "Automatically Quarantine detected threats": true,
          "Scan Suspicious filetypes only": true,
          "Auto disable suspicious startup items": false,
          "Clean temp files older than 24 hours only": true
        },
        userPath: basePath + "/config/"
      });
      var statMsg = document.getElementById('statMsg');
      var cssVariables = document.querySelector(':root');
      var compStyles = getComputedStyle(cssVariables);
      if(!store.get("Real Time Protection")){
        // Reversing value to create reverse animation
        cssVariables.style.setProperty('--scaleAt0', 1.4);
        cssVariables.style.setProperty('--scaleAt100', 1);
        cssVariables.style.setProperty('--xylentPrimary', '#FF1E00');
        statMsg.innerHTML = "At Risk!";
      }else{
        cssVariables.style.setProperty('--scaleAt0', 1);
        cssVariables.style.setProperty('--scaleAt100', 1.4);
        cssVariables.style.setProperty('--xylentPrimary', '#00B01D');
        statMsg.innerText = "System is Secure"
      }

      // Set dashboard statistics
      const statStore = new Store({
        configName: "system_stats",
        defaults: {
          "Threats Blocked": 0,
          "Items Scanned": 0
        },
        userPath: basePath + "/config/"
      })
      document.getElementsByClassName("dashboard_stat_count")[0].innerText = statStore.get("Threats Blocked");
      document.getElementsByClassName("dashboard_stat_count")[1].innerText = statStore.get("Items Scanned");
    })
  },[])
  
  return (
    <div className="flex_col">
      <h3 style={{ "textAlign": 'center' }}>Welcome to Xylent Antivirus!</h3>
      <div className="flex_row just_cent">
        <div>
          <div className="circle">
            <div className="checkMark"></div>
          </div>
        </div>
        <div className='flex_col just_cent' style={{ 'marginLeft': '35px' }}>
          <p id="statMsg" style={{ 'fontSize': '30px'}}>System is Secure</p>
          <button onClick={routeChange} id="homeScanNow_Btn">Scan Now</button>
        </div>
      </div>
      <br />
      <div className='flex_row spc_btwn'>
        <fieldset id='dashboard_status'>
          <legend>Previous Scan</legend>
          <div className='flex_col'>
            <div>
              <p className='just_cent' style={{ 'textAlign': 'center', 'fontSize': '20px', 'margin': '10px' }}><span className='dashboard_stat_count'>X</span><br /><span style={{'fontSize':'15px'}}>Threats Blocked</span></p>
              <br/>
              <p className='just_cent' style={{ 'textAlign': 'center', 'fontSize': '20px', 'margin': '10px' }}><span className='dashboard_stat_count'>X</span><br /><span style={{ 'fontSize': '15px' }}>Items Scanned</span></p>
            </div>
          </div>
        </fieldset>
        <fieldset id='dashboard_tools'>
          <legend>Tools</legend>
          <div className='flex_row just_cent' style={{'marginTop':'40px'}}>
            <div className='dashboard_tools_item flex_row just_cent' style={{ 'marginTop': '-80px', 'marginRight': '40px' }}>
              <Link>
                <span className='dashboard_tools_info'>Scan</span>
                <RiScanLine className='dashboard_tools_icon' size="22"/>
              </Link>
            </div>
            <div className='dashboard_tools_item flex_row just_cent' style={{ 'marginTop': '50px', 'marginRight': '40px' }}>
              <Link to="/optimize">
                <span className='dashboard_tools_info'>Startup<br />Monitor</span>
                <TbHeartRateMonitor className='dashboard_tools_icon' size="22"/>
              </Link>
            </div>
            <div className='dashboard_tools_item flex_row just_cent' style={{ 'marginTop': '-80px', 'marginRight': '40px' }}>
              <Link>
                <span className='dashboard_tools_info'>Junk<br />Cleaner</span>
                <LuTrash className='dashboard_tools_icon' size="22"/>
              </Link>
            </div>
            <div className='dashboard_tools_item flex_row just_cent' style={{ 'marginTop': '50px' }}>
              <Link>
                <span className='dashboard_tools_info'>Update</span>
                <div className='flex_col'>
                  <span className='dashboard_tools_icon' style={{ 'fontSize': '20px', 'fontWeight':'900' }}>&#10554;</span>
                  <span className='dashboard_tools_icon' style={{ 'fontSize': '20px','fontWeight':'900','marginTop':'-10px'}}>&#10555;</span>
                </div>
              </Link>
            </div>
          </div>
        </fieldset>
      </div>
      {/* <h2 id="nowScanning">{currScan}</h2> */}
    </div>
  )
}

export default Status