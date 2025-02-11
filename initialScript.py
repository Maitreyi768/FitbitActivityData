import pyodbc
import json
import requests
from datetime import datetime

# Header with access token and API endpoint 
api = "https://api.fitbit.com/1/user/-/activities/list.json?afterDate=2025-01-01&sort=asc&offset=0&limit=100"
header = {
    "Authorization": "Bearer {Replace this with access token}", #Replace with access token
    "Accept-Type": "application/json"
}

#Create a new database called AcitivityData if it does not already exist
connection = (
        'Driver={ODBC Driver 17 for SQL Server};'
        'Server=MAITREYI\SQLEXPRESS;' #Replace with server name
        'Database=master;'
        'Trusted_Connection=yes;'
        )

conn = pyodbc.connect(connection,autocommit = True)
cursor = conn.cursor()

cursor.execute('''
IF NOT EXISTS (
    SELECT name
        FROM sys.databases
        WHERE name = N'Activities')
CREATE DATABASE Activities ''')

cursor.close()
conn.close()

#Connect to the new database called Activities
new_db_connection = (
    'Driver={ODBC Driver 17 for SQL Server};'
    'Server=MAITREYI\SQLEXPRESS;'
    'Database=Activities;'
    'Trusted_Connection=yes;'
)

conn = pyodbc.connect(new_db_connection)
cursor = conn.cursor()

#Create a table called Activity with info about the activities the user has performed
newTable = """
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Activity' AND xtype='U')
CREATE TABLE Activity (
    StartTime DATETIME NOT NULL PRIMARY KEY,
    ActiveDurationSeconds INT NOT NULL, 
    ActivityName VARCHAR(60),
    Steps INT NOT NULL,
    PaceSecondsPerMetre FLOAT, 
    SpeedMetresPerSecond FLOAT, 
    AverageHeartRate INT,
    DistanceMetres FLOAT, 
    SedentarySeconds INT,
    LightlyActiveSeconds INT,
    FairlyActiveSeconds INT,
    VeryActiveSeconds INT
);
"""

cursor.execute(newTable)
conn.commit()

#Parse through the response to get the necessary fields

activityrequest = requests.get(api, headers=header)
if activityrequest.status_code == 200:
    responseJson = activityrequest.json() 

    for activity in responseJson["activities"]:
        #Get the starttime
        starttime = datetime.fromisoformat(activity["startTime"].replace("Z", "+00:00")) 
        
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
       

else:
    print("Response Code is not 200")

conn.commit()
cursor.close()
conn.close()
print("Completed")

