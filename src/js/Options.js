import { useLocation,useNavigate,Link} from "react-router-dom";
import {useState,useEffect} from "react";
import {useApiRequest} from './useApiRequest';
import Store from '../../store';

function Options() {
  const { state } = useLocation();
  let navigate = useNavigate();
  const routeChange = (scnTyp) => {
    console.log(scnTyp);
    let path = `/scanUI`;
    navigate(path, { state: { scanType: scnTyp } });
  }
  const [userPreference, setUserPreference] = useState({})
  var configType;
  var SLICE_START, SLICE_LIMIT;
  if (state.prevPath) {
    if (state.prevPath === "/status" || state.prevPath === "/") {
      // First 5 settings
      SLICE_START = 0;
      SLICE_LIMIT = 5;
    }
    else{
      configType = state.prevPath.split(":");
      configType = configType[1];
      if(configType=="Protection"){
          SLICE_START = 5
          SLICE_LIMIT = SLICE_START + 6
      }
      else if(configType=="Performance"){
        SLICE_START = 10
        SLICE_LIMIT = SLICE_START+2
      }
    }
  }

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
    userPath: "./backend" + "/config/"
  });
  var storeUserPreference = (id,checked) => {
    console.log(id);
    console.log(checked);
    store.set(id,checked);
    
    useApiRequest('http://127.0.0.1:5000/setUserSetting', 'POST', { setting: id, value: checked }).then(data => console.log(data))
  }
  useEffect(() => {
    console.log(state.prevPath);
    if (configType==="Protection"||configType==="Performance"||configType==="Privacy"||state.prevPath === "/status"||state.prevPath==="/"){
      var getData = () => {
        var data = store.getAll();
        console.log(data);
        return data
      }
      setUserPreference(getData());
    }
  },[])
  

  return (
    <div className={!state.prevPath ? "flex_row spc_arnd" : "flex_col spc_arnd"}>
      {userPreference && state.prevPath ?
            Object.keys(userPreference).slice(SLICE_START,SLICE_LIMIT).map((key, index) => {
              // console.log(userPreference.Home[key]);
              return (
                <div key={key} style={{'margin':'5px'}}>
                    <div className="flex_row spc_btwn">
                      <div>{key}</div>
                      <label className="toggle">
                        <input type="checkbox" id={key} defaultChecked={userPreference[key]} onClick={(e) => storeUserPreference(e.target.id, e.target.checked)} />
                        <span className="toggle_slider"></span>
                      </label>
                    </div> 
                </div>
              )
            })
            :
              Object.keys(state).map((key, index) => {
                return (
                  <div key={key}>
                    {state[key].endpoint==="scan"?   
                      <button className='statBox_height statBox_btn'  id={key} onClick={(e) => routeChange(e.target.id)}>
                        <div id={key} className='statBox flex_col spc_btwn'>
                          <div>{key} Scan</div>
                          <div className='smallFnt'>{state[key].desc}</div>
                        </div>
                      </button>
                    :
                      <Link className='statBox_height' to="/sserenderer" state={state[key]} tabIndex='-1'>
                        <div className='statBox flex_col spc_btwn'>
                          <div>{key}</div>
                        </div>
                      </Link>
                    }
                  </div>
                )
              })
      }
    </div>
  )
}

export default Options;