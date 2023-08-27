import { useLocation, Link } from "react-router-dom";
function Options() {
  const { state } = useLocation();
  var configType;
  if (state.prevPath) {
    configType = state.prevPath.split(":")
    if (configType.length > 1) {
      configType = configType[1];
    }
  }
  return (
    <div className={!state.prevPath ? "flex_row spc_arnd" : "flex_col spc_arnd"}>
      {state.prevPath === "/status" || state.prevPath === "/" ?
        Object.keys(state.config.Home).map((key, index) => {
          console.log(state.config.Home[key]);
          return (
            <div key={key}>
              {state.config.Home[key].type === "toggle" ? 
                <div className="flex_row spc_btwn">
                  <div>{key}</div>
                  <label className="toggle">
                    <input type="checkbox" defaultChecked={state.config.Home[key].value} />
                    <span className="toggle_slider"></span>
                  </label>
                </div> : <>Different Type</>}
            </div>
          )
        })
        :
        state.prevPath ?
          Object.keys(state.config[configType]).map((key, index) => {
            return (
              <div key={key}>
                {state.config[configType][key].type === "toggle" ? 
                  <div className="flex_row spc_btwn" style={{width:'500px;',marginBottom:'15px;'}}>
                    <div>{key}</div>
                    <div>
                      <label className="toggle">
                        <input type="checkbox" defaultChecked={state.config[configType][key].value} />
                        <span className="toggle_slider"></span>
                      </label>
                    </div> 
                </div> 
                : <>TODO: Add other type</>}
              </div>
            )
          })
          :
          Object.keys(state).map((key, index) => {
            return (
              <div key={key}>
                <Link className='statBox_height' to="/sserenderer" state={state[key]} tabIndex='-1'>
                  <div className='statBox flex_col spc_btwn'>
                    <div>{key}</div>
                  </div>
                </Link>
              </div>
            )
          })}
    </div>
  )
}

export default Options;