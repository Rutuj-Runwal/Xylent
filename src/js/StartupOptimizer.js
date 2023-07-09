import React from 'react';
import { useState,useEffect } from 'react';

function StartupOptimizer() {
  const [startupData, setStartupData] = useState([]);
  var toggle = (id,state) => {
    var tg_to = false;
    if(state==='on'){
      tg_to = true;
    }else{tg_to = false;}
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ toggleTo: tg_to , val:id})
    };
    fetch('http://127.0.0.1:5000/toggleItemsForStartup', requestOptions)
      .then(response => response.text())
      .then(data => console.log(data));
      
    fetchStartUPItms();
  }

  var fetchStartUPItms = () => {
    fetch('http://127.0.0.1:5000/getStartUpItems').then(
      (data) => data.json()
    ).then(
      (resp) => {
        setStartupData(resp)
      }
    )
  }
  useEffect(()=>{fetchStartUPItms()}, []);
  
  return (
    <table style={{ 'display': 'flex', 'flexDirection': 'column','tableLayout':'fixed'}}>
      {
        startupData.map((val) => {
          console.log(val);
          return (<tr style={{ 'display': 'flex', 'flexDirection': 'row','justifyContent': 'space-between','alignContent':'space-between'}}><td style={{"width":"150px"}} key={val[0]}>{val[0]}</td><td>Safe/Unsafe</td><td>{val[1] === false ? <button id={val[0]} onClick={(e) => toggle(e.target.id, "on")}>Enable</button> : <button id={val[0]} onClick={(e) => toggle(e.target.id, "off")}>Disable</button>}</td></tr>)
        
        })
      }
    </table>
  )
}

export default StartupOptimizer