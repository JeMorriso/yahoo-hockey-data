import json
import os

credentials = {
    'consumer_key': os.getenv("CONSUMER_KEY"),
    'consumer_secret': os.getenv("CONSUMER_SECRET")
}

with open('../../credentials.json', 'w') as creds_file:
    json.dump(credentials, creds_file, indent=2)