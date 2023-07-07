import React from 'react';
import {
  Link,useNavigate,useLocation
} from "react-router-dom";

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const menuOptions = {
    Protection: { 'Virus Scans': { link: "/scanChooser", desc: "Run a Quick,Full or Custom Scan" }, "Advanced Scan": { link: 'NA', desc: 'Launch Microsoft MSRT tool to scan the system', programPath: "C:\\Windows\\System32\\MRT.exe" }, 'Firewall++': { link: "/options", desc: "Enhance windows firewall with custom rules", data: { "Apply Antimalware Rules": { endpoint: "addFirewallRules", link: "https://malware-filter.gitlab.io/malware-filter/urlhaus-filter-online.txt" }, "Apply Bot Protection": { endpoint: "addFirewallRules", link: "https://feodotracker.abuse.ch/downloads/ipblocklist.txt" }, "Phishing Protection": {endpoint: "addFirewallRules", link:"https://malware-filter.gitlab.io/malware-filter/phishing-filter.txt"}}}},
    Performance: { 'Startup Monitor': { link: "/optimize", desc: "Manage Startup Items" }, "Delete Junk Files": { endpoint:"cleanJunk",link:"/sserenderer",desc:"Remove Junk Files"}},
    Privacy: { 'Microphone': { link: 'NA', desc: 'Modify microphone access', commandData: { program: 'Powershell', command: "Start ms-settings:privacy-microphone" } }, 'Camera': { link: 'NA', desc: 'Modify webcam access', commandData: { program: 'Powershell', command: "Start ms-settings:privacy-webcam" }}, 'RRAdblocker': { link: 'NA', externalLink: 'https://rutuj-runwal.github.io/RRAdblocker/', desc: 'Adblocking, Tracker and Malware Protection' } }
  }  
  return (
    <>
      {!(location.pathname === "/status" || location.pathname === "/") ? <button className='sideBar_BackNav' onClick={() => navigate(-1)}>&#8592;</button> : <></>}
      <Link to="/status" className='sideBar_Item_link' tabIndex="-1">
        <div className="flex_row just_cent sideBar_Item">Status</div>
      </Link>
      <hr/>
      <Link to="/mainFrame" state={menuOptions.Protection} className='sideBar_Item_link' tabIndex="-1">
        <div className="flex_row just_cent sideBar_Item">Protection</div>
      </Link>
      <hr />
      <Link to="/mainFrame" state={menuOptions.Privacy} className='sideBar_Item_link' tabIndex="-1">
        <div className="flex_row just_cent sideBar_Item">Privacy</div>
      </Link>
      <hr />
      <Link to="/mainFrame" className='sideBar_Item_link' state={menuOptions.Performance} tabIndex="-1">
        <div className="flex_row just_cent sideBar_Item">Performance</div>
      </Link>
      <hr />
      <div className="flex_row just_cent sideBar_Item">Settings</div>
    </>
  )
}
export default Sidebar;