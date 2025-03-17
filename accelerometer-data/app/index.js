import { outbox } from "file-transfer";
import document from 'document';
import { Accelerometer } from "accelerometer";

//Get the buttons by their id
const recordButton = document.getElementById('recordButton');
const stopRecordingButton = document.getElementById('stopButton');
//Add text (start and stop recording)
recordButton.text = 'START RECORDING';
stopRecordingButton.text = 'STOP RECORDING';
//set recording to fale
let recording = false;

// set frequency in Hz 
const freq = 1; 

//set the period for each batch i.e. 20 seconds for each batch
const timeForBatch = 20

//set the total number of readings which will be generated
const totalRecords = freq * timeForBatch; 

//set variables needed for simulator
let time;
let recordCounter = 0;
let batchcount = 0;
let acceleratorSimulator;
let simulator = true;

//initiate fitbit accelerometer (this will be used if real fitbit device is being used)
let accelerator = new Accelerometer({ frequency: freq, batch: totalRecords });


// batched data will store the batched readings
let batchedData = [];

// Add event listeners
recordButton.addEventListener("click", recordingStart);
stopRecordingButton.addEventListener("click", recordingStop);
accelerator.addEventListener("readings", transferFitbitData)

// Starts reading the simulator's/fitbit device's accelerometer readings
function recordingStart() {
    if (recording) return;
    console.log("Recording started");
    recording = true;
    recordButton.style.fill = "green";
    stopRecordingButton.style.fill = "black";
    if (simulator) {
        // reset variables
        recordCounter = 0;
        batchcount = 0;
        batchedData = []; 
        // start the simulated data
        acceleratorSimulator = setInterval(simulateBatchReading, timeForBatch * 1000); // Every 2 minutes
    } else {
        //reset variables
        batchedData = []; 
        //start the accelerator
        accelerator.start()
    }
}

//stops reading the simulator's/fitbit device's accelerometer readings and saves these to a file
function recordingStop() {
    if (recording) {
        console.log('Recording Stopped');
        recording = false;
        recordButton.style.fill = "black";
        stopRecordingButton.style.fill = "green";
        if (simulator){

            clearInterval(acceleratorSimulator);
            console.log("stopped simulating accelerometer data")

        } else {
            accelerator.stop();
            console.log("Accelerometer stopped")
        }
        
        // Save the batched data
        transferBatchedData();
    }
}

// simulates batched readings of accelerometer data 
function simulateBatchReading() {
    batchcount++;
    console.log('The batch count is: ${batchcount}');

    let batch = { timestamp: [], x: [],y: [],z: []};

    for (let i = 0; i < totalRecords; i++) {

        // generate simulated accerelormater readings
        
        time = Date.now();
        const xValue = Math.random() * 100;
        const yValue = Math.random() * 100;
        const zValue = Math.random() * 100;

        // Store simulated readings in batch
        batch.timestamp.push(time);
        batch.x.push(Math.round(xValue));
        batch.y.push(Math.round(yValue));
        batch.z.push(Math.round(zValue));
        console.log(batch);
        recordCounter++;
    }

    // Store the batch in batchedData
    batchedData.push(batch);

    console.log('Batch #${batchcount} has been stored.');
    console.log("Batch: ", JSON.stringify(batch, null, 3));

    // Save and transfer batched data
    if (batchcount >= 1) { 
        transferBatchedData();
    }
}

// if fitbit device is being used store the batches in the correct format to be transferred
function transferFitbitData() {
    batchcount++;
    let batch = {timestamp: [], x: [],y: [],z: []};
    // store batch data in correct format
    for (let index = 0; index < accel.readings.timestamp.length; index++) {
        batch.timestamp.push(accel.readings.timestamp[index]);
        batch.x.push(Math.round(accel.readings.x[index]));
        batch.y.push(Math.round(accel.readings.y[index]));
        batch.z.push(Math.round(accel.readings.z[index]));
    }
    batchedData.push(batch)

    //Save and transfer batch data
    if (batchcount >= 1) { 
        transferBatchedData();
    }

}



function transferBatchedData() {
    // Convert batched data to json 
    const jsonData = JSON.stringify(batchedData, null, 2);

    // Unique file name is generated using timestamp
    const timestamp = Date.now(); 
    let fileName = '${timestamp}.json';

    // convert json to buffer (accepted format for outbox)
    const arrayBuffer = convertStrtoBuffer(jsonData);

    // use file transfer api to push the file into a queue which can be accessed by companion api
    outbox.enqueue(fileName, arrayBuffer)
        .then((file) => {
            console.log(' ${file.name} has successfuly been enqueued');
        })
        .catch((error) => {
            console.log('Can not add to queue: ${error}');
        });

    // reset batched data
    batchedData = [];
}

// manually converts string to buffer
function convertStrtoBuffer(str) {

    const buffer = new ArrayBuffer(str.length);
    const view = new Uint8Array(buffer);
    for (let i = 0; i < str.length; i++) {
        view[i] = str.charCodeAt(i);
    }
    return buffer;
}
