import { useLocation,Link } from "react-router-dom";
import { useState } from 'react'
function Options() {
  const { state } = useLocation();
  
  return (
    <div className="">
    <div className = 'flex_row spc_arnd'>
        {Object.keys(state).map((key, index) => {
          return (
            <div key={key}>
              <Link className='statBox_btn statBox_height' to="/sserenderer" state={state[key]} tabIndex='-1'>
                <div className='statBox flex_col spc_btwn'>
                    <div>{key}</div>
                </div>
              </Link>
            </div>
          )
        })}
    </div>
    </div>
  )
}

export default Options;