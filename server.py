from flask import Flask,request
from datetime import datetime, timedelta
import json
import requests
import pyodbc
import threading
import os 
import csv


app = Flask(__name__)

lock = threading.Lock()
def sendRequest():
    print("sending request")
    today = datetime.strftime(datetime.now()), '%Y-%m-%d')
    api = f"https://api.fitbit.com/1/user/-/activities/list.json?afterDate={today}&sort=asc&offset=0&limit=100"
    header = {
        "Authorization": "Bearer {Replace with access token}", #Replace here with access token
        "Accept-Type": "application/json"
    }
    with lock:
        print("Sending request...")
        activityrequest = requests.get(api, headers=header)
        if activityrequest.status_code != 200:
            return
            
        db_connection = (
            'Driver={ODBC Driver 17 for SQL Server};'
            'Server=MAITREYI\SQLEXPRESS;' #Replace with server name
            'Database=Activities;'
            'Trusted_Connection=yes;'
        )
        try:
            conn = pyodbc.connect(db_connection)
            cursor = conn.cursor()

            # Fetch start times from the database
            query = f"""
            SELECT StartTime 
            FROM Activity
            WHERE StartTime > '{yesterday}'
            """
            cursor.execute(query)
            db_start_times = {row[0] for row in cursor.fetchall()}

            for item in db_start_times:
                print(item)
                
            
            responseJson = activityrequest.json() 

            for activity in responseJson["activities"]:
                starttime = datetime.fromisoformat(activity["startTime"].replace("Z", "")) 
                print(starttime)
                
                #Check if it's already stored
                if starttime not in db_start_times:
                    print("adding")
                    #Get the active duration and convert to secs
                    activeduration = activity["activeDuration"] / 1000
                    
                    #Get the activity name e.g. Run
                    activityname = activity["activityName"]
                    
                    #Get the number of steps
                    steps = activity["steps"]
                    
                    #Get the pace and convert to S/M
                    pace = activity.get("pace", None) 
                    if (pace != None) :
                         pace = round(pace/1000, 2)
                         
                    #Get the speed and convert to M/S
                    speed = activity.get("speed", None) 
                    if (speed != None) :
                         speed = round(speed / 3.6, 2)
                         
                    #Get the average heart rate
                    averageheartrate = activity.get("averageHeartRate", None)
                    
                    #Get the distance and convert to metres
                    distanceM = activity.get("distance", None)
                    if (distanceM != None):
                       distanceM = round(distanceM * 1000, 2)
                       
                    #Get the activity levels and convert to seconds
                    array = activity["activityLevel"]
                    outputdict = [x for x in array if x['name'] == 'sedentary']
                    sedentarymins = outputdict[0]["minutes"] * 60
                    outputdict2 = [x for x in array if x['name'] == 'fairly']
                    fairlyactivemins = outputdict2[0]["minutes"] * 60
                    outputdict3 = [x for x in array if x['name'] == 'very'] 
                    veryactivemins = outputdict3[0]["minutes"] * 60
                    outputdict4 = [x for x in array if x['name'] == 'lightly']
                    lightlyactivemins = outputdict4[0]["minutes"] * 60
                    
                    #Insert the values into the table
                    cursor.execute("""
                    INSERT INTO Activity (
                        StartTime, ActiveDurationSeconds, ActivityName, Steps, PaceSecondsPerMetre, SpeedMetresPerSecond, AverageHeartRate, 
                        DistanceMetres, SedentarySeconds, LightlyActiveSeconds, FairlyActiveSeconds, VeryActiveSeconds
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        starttime, activeduration, activityname, steps, pace, speed,
                        averageheartrate, distanceM, sedentarymins, lightlyactivemins,
                        fairlyactivemins, veryactivemins
                    ))
                        
            conn.commit()
        except pyodbc.Error as e:
            logging.error(f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()
    

    

def save_to_csv(data):
 
    # Check if the CSV file exists
    exists = os.path.exists('accelerometer_data.csv')
    
    # Open csv file accelerometer_data
    with open('accelerometer_data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write headers for new file
        if not exists:
            writer.writerow(['timestamp', 'x', 'y', 'z'])
        
        # Data should be a list of dictionaries
        if isinstance(data, list):
            # Extract data
            batchData = data[0]

            # Validates that x, y, z are lists consisting of accelerometer data
            if isinstance(batchData.get('x'), list) and isinstance(batchData.get('y'), list) and isinstance(batchData.get('z'), list):
                # Write each row of data
                for i in range(len(batchData['x'])):
                    row = [ batchData['timestamp'][i],batchData['x'][i],batchData['y'][i],batchData['z'][i]]
                    writer.writerow(row)
            else:
                print("Incorrect format")
        else:
            print("Error")

    
@app.route('/', methods = ['POST'])
def postRequestRecieved():
    if request.method == 'POST':
        # Check if binary data has been sent from accelerometer
        if request.content_type == 'application/octet-stream':
            # Get the binary data
            file_data = request.data  

            # Decode the binary data 
            try:
                decoded_data = file_data.decode('utf-8')  
                print(decoded_data)  
                data = json.loads(decoded_data)
                save_to_csv(data)

            except UnicodeDecodeError:
                # If the binary data cannot be decoded as a string, it may be a non-text file
                print("Data can not be decoded")

            return 'Data has been successfully recieved by the server', 200
        
        else:
            # Get the webhook request
            data = request.get_json()  
            print("Received JSON data:", data)

            # send request to get new data from database
            sendRequest()

            return 'success', 200

    else:
        return {"message": "Only POST requests are allowed"}, 405

if __name__ == '__main__':
    app.run()