
# FitbitActivityData

This repository pulls activity data from Fitbit and stores it in SQL Server.

## Installment Requirements

1. **Download Python (version > 3.10)**  
   [Link: Python Downloads](https://www.python.org/downloads/)

2. **Download ngrok**  
   [Link: ngrok Downloads](https://ngrok.com/downloads/windows?tab=download)

3. **Download SQL Server**  
   [Link: SQL Server Downloads](https://www.microsoft.com/en-gb/sql-server/sql-server-downloads)

4. **Download SQL Server Management Studio**  
   [Link: SSMS Downloads](https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms?view=sql-server-ver16)

## Account Requirements

1. **Fitbit Developer Account**  
   [Link: Fitbit Developer](https://dev.fitbit.com/)

2. **Pipedream Account**  
   [Link: Pipedream](https://pipedream.com/)

## Getting Started

### 1) Register an App in Fitbit Developer Account

Provide the following details during the registration process:

- **Application Name**
- **Description**
- **Application Website URL**
- **Organization**
- **Organization Website URL**
- **Terms of Service URL**
- **Privacy Policy URL**
- **OAuth 2.0 Application Type**
- **Redirect URL**
- **Default Access Type**

**Note:** The URLs (except the Redirect URL) can be random.  
- Set **Redirect URL** to `http://localhost`
- Set **OAuth 2.0 Application Type** to `Personal`
- Set **Default Access Type** to `Read Only`

Example registration:

![Sample Registration of app](assets/images/RegisterApp.png)

---

### 2) Follow the OAuth 2.0 Tutorial to Get Access Keys

Make sure to follow the tutorial linked in your Fitbit developer account to retrieve the required access keys:

![Follow the link provided](assets/images/oauth.png)

---

### 3) Verify Subscriber (Add Pipedream Details Here)

- Add details here

---

### 4) Replace Keys in `initialScript.py`

- Open `initialScript.py` and replace the key where indicated.
- Run the script in the command line using the following command:

```bash
python initialScript.py
```

This should create the **Activities** database and the **Activity** table:

![Database Created](assets/images/databasecreated.png)

---

### 5) Create an ngrok Endpoint

- Run ngrok to expose port 8000:

```bash
ngrok http 8000
```

This will expose port 80, allowing it to receive requests from the Pipedream URL.

---

### 6) Replace Key in `server.py`

- Open `server.py` and replace the key where indicated.
- Run the server script using the following command:

```bash
python server.py
```

---

### 7) Edit Activity Data Using Fitbit

- Complete an activity and wear the Fitbit. Keep the Fitbit app open on your phone to immediately sync the data with your account.
- This should update the **Activity** table successfully.
