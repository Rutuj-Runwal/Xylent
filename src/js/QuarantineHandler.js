import {useEffect,useState} from 'react';
import Store from '../../store';
import { ipcRenderer} from 'electron';
function QuarantineHandler() {
    const [quarantineData, setquarantineData] = useState([]);
    var restoreQuar = (id) => {
        console.log("Restoring: "+id)
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ originalPath: id })
        };
        fetch('http://127.0.0.1:5000/restoreFile', requestOptions)
            .then(response => response.text())
            .then(data => console.log(data))
            .then(() => window.location.reload());
    }
    var removeQuar = (id) => {
        console.log("Deleting: " + id);
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ originalPath: id })
        };
        fetch('http://127.0.0.1:5000/removeFile', requestOptions)
            .then(response => response.text())
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
                            <td><button id={val} className='itemStatusPill' style={{ 'backgroundColor':"lightgrey" }} onClick={(e) => restoreQuar(e.target.id)}>Restore</button></td>
                            <td><button id={val} className='itemStatusPill' style={{ 'backgroundColor':'lightblue'}} onClick={(e) => removeQuar(e.target.id)}>Delete</button></td>
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