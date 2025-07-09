import os
import requests
from notion_client import Client
from dotenv import load_dotenv

def get_assignments():
    return assignments

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

# Get data from Notion database
response = requests.post(url, headers=headers, json=status_filter)
if response.status_code == 200:
    data = response.json()
    results = data.get("results", [])
else:
    print("Failed to return data from Notion API: ", response.text)

assignments = []
# Get the properties of each assignment page
for page in results:
    properties = page["properties"]
    name = properties["Name"]["title"][0]["text"]["content"] if properties["Name"]["title"] else "Untitled"
    due_date = properties["due date"]["date"]["start"] if properties["due date"]["date"] else "No due date"
    course = properties["course"]["multi_select"][0]["name"] if properties["course"]["multi_select"] else "No course"
    type = properties["type"]["multi_select"][0]["name"] if properties["type"]["multi_select"] else "No type"

    assignment = {
        "name": name,
        "due_date": due_date,
        "course": course,
        "type": type
    }
    assignments.append(assignment)