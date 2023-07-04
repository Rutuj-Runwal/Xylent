import { useLocation } from "react-router-dom";

function Options() {
  const { state } = useLocation();
  var addFirewallRules = async (key) => {
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ link: state[key].link })
    };
    console.log(state[key].link);
    var data = await fetch('http://127.0.0.1:5000/addFirewallRules', requestOptions)
    var parsed = await data.text()
    console.log(parsed);
    // TODO: Add a modal UI for confirmartion
  }
  return (
    <div className="">
    <div className = 'flex_row spc_arnd'>
        {Object.keys(state).map((key, index) => {
          return (
            <div key={key}>
              <button className='statBox_btn statBox_height' onClick={() => addFirewallRules(key)} tabIndex='-1'>
                <div className='statBox flex_col spc_btwn'>
                    <div>{key}</div>
                </div>
              </button>
            </div>
          )
        })}
    </div>
    </div>
  )
}

export default Options;