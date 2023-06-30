import React from 'react';
import {
  Link
} from "react-router-dom";


function Sidebar() {

  const menuOptions = {
    Protection: { 'Virus Scans': { link: "/scanChooser", desc: "Run a Quick,Full or Custom Scan" }, "Advanced Scan": { link: 'NA', desc: 'Launch Microsoft MSRT tool to scan the system', programPath:"C:\\Windows\\System32\\MRT.exe"}},
    Performance:{'Startup Monitor':{link:"/optimize",desc:"Manage Startup Items"},"Delete Junk Files":{link:"/deleteJunk",desc:"Remove Junk Files"}}
  }  
  return (
    <>
      <Link to="/status" className='sideBar_Item_link' tabIndex="-1">
        <div className="flex_row just_cent sideBar_Item">Status</div>
      </Link>
      <hr/>
      <Link to="/mainFrame" state={menuOptions.Protection} className='sideBar_Item_link' tabIndex="-1">
        <div className="flex_row just_cent sideBar_Item">Protection</div>
      </Link>
      <hr />
      <div className="flex_row just_cent sideBar_Item">Privacy</div>
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