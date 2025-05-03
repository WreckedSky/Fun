## How to use?

You will need a credentials.json
And how?

Create a Google Cloud Project:

- Go to the Google [Cloud Console](https://console.cloud.google.com)
- Create a new project
- Enable the Google Sheets API

For enabling Google Sheets API:

- Go to "APIs & Services" > "Library"
- Search for "Google Sheets API" and enable it
- Create Service Account Credentials

For creating Service account Credentials
- Go to "APIs & Services" > "Credentials"
- Click "Create Credentials" > "Service Account"
- Fill in the service account details and click "Create"
- Grant this service account appropriate roles (like "Editor")
- Click "Done"
- Generate JSON Key

For generating JSON Key:
- Find your service account in the list
- Click on it, then go to the "Keys" tab
- Click "Add Key" > "Create new key"
- Select "JSON" format and click "Create"
- The JSON key file will download automatically
- Save the downloaded file as credentials.json in the same directory as your Python script



