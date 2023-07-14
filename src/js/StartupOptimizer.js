import { useState,useEffect } from 'react';
import { IconContext } from 'react-icons';
import { IoCloseCircle, IoCheckmarkCircle, IoWarning } from "react-icons/io5";
import { RxQuestionMarkCircled } from "react-icons/rx";

function StartupOptimizer() {
  const [startupData, setStartupData] = useState([]);
  var toggle = (id,state) => {
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ toggleTo: state, val: id })
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
    <table style={{ 'display': 'flex', 'flexDirection': 'column', 'tableLayout': 'fixed', 'borderCollapse': 'collapse', 'borderSpacing': '0', 'width': '650px' }}>
        <tr style={{ 'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'space-between'}}>
          <th style={{ 'width': '200px', 'marginRight': '5px', 'padding': '0 !important' }}>Name</th>
          <th>Analysis</th>
          <th>Enable/Disable</th>
        </tr>
        {
          startupData.map((val) => {
            console.log(val);
            return (
              <tr style={{ 'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'space-between', 'alignItems': 'center'}}>
                <td style={{ 'width': '200px', 'padding': '0 !important','fontWeight':'500' }} key={val[0]}>
                  {val[0]}
                </td>
                <td>
                  <div className='itemStatusPill' style={{ 'backgroundColor': val[2] === "Safe" ? "#00B01D" : val[2] === "Suspicious" ? "lightyellow" : val[2] === "Malware" ? "red" : "lightgrey" }}>
                    {val[2]}
                  </div>
                </td>
                <td>
                    <label className="toggle">
                      <input type="checkbox" id={val[0]} defaultChecked={val[1]} onChange={(e) => toggle(e.target.id,e.target.checked)}/>
                        <span className="toggle_slider"></span>
                    </label>
                </td>
              </tr>
            )

          })
        }
    </table>
  )
}

export default StartupOptimizer