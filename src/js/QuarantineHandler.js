import {useEffect,useState} from 'react';
import { useApiRequest } from './useApiRequest';
import Store from '../../store';
import { ipcRenderer} from 'electron';
function QuarantineHandler() {
    const [quarantineData, setquarantineData] = useState([]);
    var handleQuar = (id,type) => {
        console.log("Handling: "+id)
        const url = type+"File"
        useApiRequest('http://127.0.0.1:5000/'+url, 'POST', { originalPath: id })
        .then(data => console.log(data))
        .then(() => window.location.reload());
    }

    useEffect(() => {
        ipcRenderer.send('xylent-get-path', "XYLENT_GET_APP_PATH");
        ipcRenderer.once('xylent-get-path', (event, basePath) => {
            const store = new Store({
                configName: "quar_info",
                defaults: {},
                userPath: basePath + "/config/"
            });
            var getData = () => {
                var data = store.getAll();
                return data
            }
            setquarantineData(getData());
        })
        
    }, []);
    
    return (
        <table>
            <tbody>
            {   
                Object.keys(quarantineData).length ?
                Object.keys(quarantineData).map((val) => {
                    return(
                        <tr key={val}>
                            <td>{val}</td>
                            <td>{quarantineData[val]}</td>
                            <td><button id={val} className='itemStatusPill' style={{ 'backgroundColor': "lightgrey" }} onClick={(e) => handleQuar(e.target.id,'restore')}>Restore</button></td>
                            <td><button id={val} className='itemStatusPill' style={{ 'backgroundColor': 'lightblue' }} onClick={(e) => handleQuar(e.target.id,'remove')}>Delete</button></td>
                        </tr>
                    )
                })
                :
                <tr>
                    <td><h4>No items in quarantined!</h4></td>
                </tr>
                
            }
            </tbody>
        </table>
    )
}

export default QuarantineHandler