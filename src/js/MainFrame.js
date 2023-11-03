import { Link, useLocation } from 'react-router-dom';
import { shell } from "electron";
import { useApiRequest } from './useApiRequest';
function MainFrame() {
    let { state } = useLocation();
    var launchProgram = async (key) => {
        var endpoint = "";
        if(state[key].programPath){
            endpoint = "/launchProgram"
        }else if(state[key].commandData){
            endpoint = "/executeCommand"
        }else{
            console.log(state[key].externlLink);
            shell.openExternal(state[key].externalLink)
        }
        
        if(endpoint){
            let bodyData = {commandData:state[key]?.commandData,programPath:state[key]?.programPath};
            console.log(bodyData);

            useApiRequest('http://127.0.0.1:5000'+endpoint, 'POST', bodyData).then(data => console.log(data));
        }
    }
    return (
        <div className='grid' style={{gridTemplateColumns:'200px 200px 200px'}}>
            {Object.keys(state).map((key, index) => {
                return (
                    <div key={key} className='statBox_btn statBox_height'>
                        {state[key].link != "NA" ?
                            <Link className='mainFrame_Lnk' to={state[key].link} state={state[key].data? state[key].data : state[key]} tabIndex="-1">
                                <div className='statBox flex_col spc_btwn'>
                                    <div className='flex_row spc_btwn'>
                                        <div>{key}</div>
                                    </div>
                                    <div className='smallFnt'>{state[key].desc}</div>
                                </div>
                            </Link>
                            :
                            <button className='mainFrame_Btn' onClick={() =>launchProgram(key)} tabIndex='-1'>
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