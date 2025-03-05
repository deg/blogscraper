# Google integration notes

## Setup instructions

### Enable Google APIs
- Go to [Google Cloud Console](https://cloud.google.com/)
- Click on `Go to my console`
- Choose a project or, recommended, create a new one.
- Navigate to APIs & Services > Library.
- Enable the following APIs: Google Docs API, Google Drive API

### Create a service account
- Navigate to APIs & Services > Credentials.
- Click "Create Credentials" and choose "Service account".
- Enter a name and description, then click Create & Continue.
- Assign the role Editor (or a more restricted role if needed).
- Click Continue and then Done.

### Generate and store the JSON Key
- Click on the newly created account in the Service Accounts list
- Go to the "Keys" tab.
- Click "Add Key" > "Create New Key".
- Choose JSON, then click Create.
- Save the downloaded .json file into <project_root>/secrets/
- **Do not commit this file to the repo. It is secret**
- Create or add a line to <project_root>/.env.secret:
  `GOOGLE_SERVICE_ACCOUNT_FILE=secrets/<NEW_FILE_NAME>.json`

## Programming tips

### Add libraries:

```
poetry add google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```
