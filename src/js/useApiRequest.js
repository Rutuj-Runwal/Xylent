const useApiRequest = (url,methodType,bodyData,responseType='text') => {
    return new Promise(async (resolve,reject) => {
        var requestOptions = {}
        if(methodType==='POST'){
            requestOptions = {
                method: methodType,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(bodyData)
            };
        }
        try{
            const response = await fetch(url, requestOptions);
            console.log(response.ok);
            console.log(response.status);
            if (!response.ok) {
                reject(new Error(`Request failed with status ${response.status}`));
            }
            if (responseType != 'text') {
                resolve(response.json());
            } else {
                resolve(response.text());
            }
        }catch(err){
            console.log(err);
            var process = url.split("/")[url.split("/").length - 1]
            alert(`Engine not running.
            Xylent Antivirus is unable to ${process}! 
            Please restart engine`);
        }
        
    })
}

export {useApiRequest}