import os
import requests
from dotenv import load_dotenv

from notion_client import Client

load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Initialize Notion client
notion = Client(auth=NOTION_API_KEY)
url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",  
    "Content-Type": "application/json"
}

# filter to retrieve assignments whose status is either "Not Started" or "In Progress"
status_filter = {
    "filter": {
        "or": [
            {
                "property": "Progress",
                "status": {
                    "equals": "Not started"
                }
            },
            {
                "property": "Progress",
                "status": {
                    "equals": "In progress"
                }
            }
        ]
    }
}

# Fetching data from Notion database
response = requests.post(url, headers=headers, json=status_filter)
if response.status_code == 200:
    data = response.json()
    results = data.get("results", [])
    print(results)
else:
    print("Failed to return data from Notion API: ", response.text)

print("Status Code:", response.status_code)
print("Response Text:", response.text)

