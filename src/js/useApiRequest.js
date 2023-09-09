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
        const response = await fetch(url,requestOptions)
        if (responseType!='text'){
            resolve(response.json());
        }else{
            resolve(response.text());
        }
    })
}

export {useApiRequest}