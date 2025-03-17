import { inbox } from "file-transfer";

// function to send file to server
async function sendFileToServer(file) {
  let fileName = file.name;

  // get the content of the file as an array buffer (binary data)
  const fileContent = await file.arrayBuffer();

  console.log('Sending POST request');

   // Send post request to local server with binary file
  fetch('http://127.0.0.1:5000', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/octet-stream', //This is used to specify the binary format being sent
      'File-Name': fileName 
    },
    body: fileContent 
  })
    .then(response => response.text())
    .then(res => {
      console.log('Successful', res);
    })
    .catch(e => {
      console.error('Error:', e);
    });

 
}
//get the new file from queue
async function getFile() {
  // get the top file from the queue
  let file = await inbox.pop();

  if (file) {
    console.log('Received file: ${file.name}');
    sendFileToServer(file);
  }
}

//call getFile when a new file is enqueued

inbox.addEventListener("newfile", getFile);


