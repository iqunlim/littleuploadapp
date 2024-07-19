const API_URL =  '/v2/sign-s3/'

// Sometimes, when you run JSON.parse it doesnt REALLY parse. This makes sure it either eventually parses or explodes and throws an error.
function reallyParse(item) {
  let ret = JSON.parse(item);
  while (typeof ret === "string") {
    ret = JSON.parse(ret);
  }
  return ret;
}
/*
  Function to carry out the actual POST request to S3 using the signed request from the Python app.
*/
function uploadFile(file, s3Data, url){
  const xhr = new XMLHttpRequest();
  xhr.open('POST', s3Data.url);
  console.log(s3Data)
  const postData = new FormData();
  for(key in s3Data.fields){
    postData.append(key, s3Data.fields[key]);
  }
  postData.append('file', file);
  xhr.onreadystatechange = () => {
    if(xhr.readyState === 4){
      if(xhr.status === 200 || xhr.status === 204){
        document.getElementById('preview').src = url;
        document.getElementById('status').innerHTML = "Uploaded. Please Check your download link below."
        document.getElementById('link').innerHTML = "URL: " + url
        document.getElementById("uploadButton").style.visibility = "hidden"; 
      }
      else{
        alert('Could not upload file.');
      }
    }
  };
  xhr.send(postData);
}

/*
  Function to get the temporary signed request from the Python app.
  If request successful, continue to upload the file using this signed
  request.
*/
function getSignedRequest(file){
  const xhr = new XMLHttpRequest();
  xhr.open('GET', `${API_URL}?fileName=${file.name}&fileType=${file.type}&t=${file.size}`);
  xhr.onreadystatechange = () => {
    if(xhr.readyState === 4){
      if(xhr.status === 200) {
        const response = reallyParse(xhr.response)
        if(response.error != "") { 
          alert(response.error)
        }
        else { 
          uploadFile(file, response.data, response.url);
        }
      }
      else{
        alert('Could not get signed URL.');
      }
    }
  };
  xhr.send();
}

/*
   Function called when file input updated. If there is a file selected, then
   start upload procedure by asking for a signed request from the app.
*/
function initUpload(){
  const files = document.getElementById('file-input').files;
  const file = files[0];
  if(!file){
    return alert('No file selected.');
  }
  getSignedRequest(file);
}

/*   Bind listeners when the page loads. Keeping this here for personal knowledge
(() => {
  document.getElementById('file-input').onchange = enableUpload;
})();*/