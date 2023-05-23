import React from 'react';
import {
  Link
} from "react-router-dom";


function Sidebar() {
  const styles = {
    flexCol: {
        display:"flex",
        flexDirection:"column",
        backgroundColor:"red",
        width:"250px",
        height:"700px"
    },
    flexRow: {
        display: "flex",
        flexDirection: "row",
        height: "124px",
        backgroundColor:"bown",
        alignItems:"center",
        justifyContent:"center"
    }
  }  
  return (
    <>
      <div style={styles.flexRow}><Link to="/status">Status</Link></div>
      <div style={styles.flexRow}>Protection</div>
      <div style={styles.flexRow}>Privacy</div>
      <div style={styles.flexRow}><Link to="/optimize">Performance</Link></div>
      <div style={styles.flexRow}>Settings</div>
    </>
  )
}
export default Sidebar;