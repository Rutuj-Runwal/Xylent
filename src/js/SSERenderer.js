import { useEffect, useState } from 'react';
import { useLocation } from "react-router-dom";
function SSERenderer() {
    const { state } = useLocation();
    const [data, setData] = useState('Initializing...')
    var fetchProgessViaSSE = async (key) => {
        console.log(state);
        var BASE_URL = "http://127.0.0.1:5000/"
        var response;
        if(state.link){
          response = await fetch(BASE_URL + state.endpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({ link: state.link })
          })
        }else{
          response = await fetch(BASE_URL + state.endpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            }
          })
        }
        const reader = response.body.pipeThrough(new TextDecoderStream()).getReader()
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            setTimeout(() => {
              console.log('Received', value);
              setData(value.split("data:")[1]);
            }, 1000);
        }
        // TODO: Add a modal UI for confirmartion
    }
    useEffect(() => {
      fetchProgessViaSSE()
    }, []);
    
  return (
    <div>
        <br/>
        {data}
    </div>
  )
}

export default SSERenderer;