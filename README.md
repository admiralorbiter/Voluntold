# Voluntold: 
In between microservice to pipe salesforce data into a volunteer sign up page.

## Setup

1. Install dependencies
```
pip install -r requirements.txt
```

2. Set up environment variables
```
SF_USERNAME=
SF_PASSWORD=
SF_SECURITY_TOKEN=
```

3. Run the app
```
python app.py
```

## Future Features
- Different pages, way to control which event goes on which page.
- When sync, if there are events in the database, that weren't in the sync list, flag for deletion.
- Delete event if the start date is in the past
- Add event to database if it doesn't exist yet.
- Add a way to control the display order of the events.
