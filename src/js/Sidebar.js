import React from 'react';
import {
  Link,useNavigate,useLocation
} from "react-router-dom";
import { IconContext } from "react-icons";
import { IoCheckmarkCircleOutline, IoShieldCheckmarkOutline, IoAnalyticsOutline, IoLockClosedOutline, IoSettingsOutline } from "react-icons/io5";
import { LuSettings  } from "react-icons/lu";

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const menuOptions = {
    BASE:{
      Protection: { 'Virus Scans': { link: "/scanChooser", desc: "Run a Quick,Full or Custom Scan" }, "Advanced Scan": { link: 'NA', desc: 'Launch Microsoft MSRT tool to scan the system', programPath: "C:\\Windows\\System32\\MRT.exe" }, 'Firewall++': { link: "/options", desc: "Enhance windows firewall with custom rules", data: { "Apply Antimalware Rules": { endpoint: "addFirewallRules", link: "https://malware-filter.gitlab.io/malware-filter/urlhaus-filter-online.txt" }, "Apply Bot Protection": { endpoint: "addFirewallRules", link: "https://feodotracker.abuse.ch/downloads/ipblocklist.txt" }, "Phishing Protection": { endpoint: "addFirewallRules", link: "https://malware-filter.gitlab.io/malware-filter/phishing-filter.txt" } } }, 'Quarantine': { link: '/manageQuars', desc: 'Manage Quarantine items' } },
      Performance: { 'Startup Monitor': { link: "/optimize", desc: "Manage Startup Items" }, "Delete Junk Files": { endpoint:"cleanJunk",link:"/sserenderer",desc:"Remove Junk Files"}},
      Privacy: { 'Microphone': { link: 'NA', desc: 'Modify microphone access', commandData: { program: 'Powershell', command: "Start ms-settings:privacy-microphone" } }, 'Camera': { link: 'NA', desc: 'Modify webcam access', commandData: { program: 'Powershell', command: "Start ms-settings:privacy-webcam" }}, 'RRAdblocker': { link: 'NA', externalLink: 'https://rutuj-runwal.github.io/RRAdblocker/', desc: 'Adblocking, Tracker and Malware Protection' } } 
    },
    CONFIGS:{
      Home:{'Real Time Protection':{type:'toggle',value:true},'Notification':{type:'toggle',value:false},'Notification Duration':{type:'choice',value:'2'},'Auto check for definition updates':{type:'toggle',value:true},'Auto check for program updates':{type:'toggle',value:true}},
      Protection:{'Scan PE files':{type:'toggle',value:true},'Apply additional checks for archives':{type:'toggle',value:true},'Treat un-signed executables as suspicious':{type:'toggle',value:true},'Automatically Quarantine detected threats':{type:'toggle',value:true},'Scan Suspicious filetypes only':{type:'toggle',value:true}},
      Performance:{'Auto disable suspicious startup items':{type:'toggle',value:false},'Clean temp files older than 24 hours only':{type:'toggle',value:true}}

    }
  }
  return (
    <>
      {!(location.pathname === "/status" || location.pathname === "/") ? <button className='sideBar_BackNav' onClick={() => navigate(-1)}>&#8592;</button> : <></>}
      <IconContext.Provider style={{strokeWidth:'10px !important',stroke:'green'}} value={{ color: "green" }}>
        {(location.pathname === "/status" || location.pathname === "/" || location.pathname.includes("/mainFrame")) ? <Link to="/options" state={{ config: menuOptions.CONFIGS, prevPath: location.pathname }}>
          <LuSettings className='sideBar_setting_icon' size={23} />
        </Link> : <></>}  
      </IconContext.Provider>
      <Link to="/status" tabIndex="-1">
        <div className="flex_row just_cent sideBar_Item"><IconContext.Provider style={{ stroke: "black", strokeWidth: "1" }} value={{ color: "green" }}><IoCheckmarkCircleOutline size={45}/></IconContext.Provider></div>
      </Link>
      <hr/>
      <Link to="/mainFrame/:Protection" state={menuOptions.BASE.Protection} tabIndex="-1">
        <div className="flex_row just_cent sideBar_Item"><IconContext.Provider value={{ color: "green" }}><IoShieldCheckmarkOutline size={45} /></IconContext.Provider></div>
      </Link>
      <hr />
      <Link to="/mainFrame/:Privacy" state={menuOptions.BASE.Privacy} tabIndex="-1">
        <div className="flex_row just_cent sideBar_Item"><IconContext.Provider value={{ color: "green" }}><IoLockClosedOutline size={35} /></IconContext.Provider></div>
      </Link>
      <hr />
      <Link to="/mainFrame/:Performance"  state={menuOptions.BASE.Performance} tabIndex="-1">
        <div className="flex_row just_cent sideBar_Item"><IconContext.Provider value={{ color: "green" }}><IoAnalyticsOutline size={45} /></IconContext.Provider></div>
      </Link>
      <hr />
      <div className="flex_row just_cent sideBar_Item"><IconContext.Provider value={{ color: "green" }}><IoSettingsOutline size={35} /></IconContext.Provider></div>
    </>
  )
}
export default Sidebar;