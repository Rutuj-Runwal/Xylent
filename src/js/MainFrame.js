import { Link, useLocation } from 'react-router-dom';
import { shell } from "electron";
function MainFrame() {
    let { state } = useLocation();
    var launchProgram = async (key) => {
        if(state[key].programPath){
            const requestOptions = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ programPath: state[key].programPath })
            };
            var data = await fetch('http://127.0.0.1:5000/launchProgram', requestOptions)
            var parsed = await data.text()
            console.log(parsed);
        }else if(state[key].commandData){
            const requestOptions = {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ commandData: state[key].commandData })
            };
            var data = await fetch('http://127.0.0.1:5000/executeCommand', requestOptions)
            var parsed = await data.text()
            console.log(parsed);
        }else{
            console.log(state[key].externlLink);
            shell.openExternal(state[key].externalLink)
        }
    }
    return (
        <div className='flex_row spc_arnd'>
            {Object.keys(state).map((key, index) => {
                return (
                    <div key={key} >
                        {state[key].link != "NA" ?
                            <Link className='statBox_btn statBox_height' to={state[key].link} state={state[key].data? state[key].data : state[key]} tabIndex="-1">
                                <div className='statBox flex_col spc_btwn'>
                                    <div className='flex_row spc_btwn'>
                                        <div>{key}</div>
                                    </div>
                                    <div className='smallFnt'>{state[key].desc}</div>
                                </div>
                            </Link>
                            :
                            <button className='statBox_btn statBox_height'onClick={() =>launchProgram(key)} tabIndex='-1'>
                                <div className='statBox flex_col spc_btwn'>
                                    <div className='flex_row spc_btwn'>
                                        <div>{key}</div>
                                    </div>
                                    <div className='smallFnt'>{state[key].desc}</div>
                                </div>
                            </button>
                        }
                    </div>
                )

            })}

        </div>
    )
}

export default MainFrame