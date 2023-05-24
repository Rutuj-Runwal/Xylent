import React from 'react';
import {
  Link
} from "react-router-dom";


function Sidebar() {
  const styles = {
  }  
  return (
    <>
      <Link to="/status" className='sideBar_Item_link' tabIndex="-1">
        <div className="flex_row just_cent sideBar_Item">Status</div>
      </Link>
      <hr/>
      <div className="flex_row just_cent sideBar_Item">Protection</div>
      <hr />
      <div className="flex_row just_cent sideBar_Item">Privacy</div>
      <hr />
      <Link to="/optimize" className='sideBar_Item_link' tabIndex="-1">
        <div className="flex_row just_cent sideBar_Item">Performance</div>
      </Link>
      <hr />
      <div className="flex_row just_cent sideBar_Item">Settings</div>
    </>
  )
}
export default Sidebar;