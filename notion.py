import os
import requests
from notion_client import Client
from dotenv import load_dotenv

def get_assignment_names():
    return [assignment["name"] for assignment in assignments]

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

# Get data from Notion database
response = requests.post(url, headers=headers, json={})
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
    notion_id = page["id"]
    progress = properties["Progress"]["status"]["name"] if properties["Progress"]["status"] else "No status"
    todoist_task_id = properties["Todoist Task ID"]["rich_text"][0]["text"]["content"] \
        if properties.get("Todoist Task ID") and properties["Todoist Task ID"]["rich_text"] else ""

    assignment = {
        "name": name,
        "due_date": due_date,
        "course": course,
        "type": type,
        "notion_id": notion_id,
        "progress": progress,
        "todoist_task_id": todoist_task_id
    }
    assignments.append(assignment)
    for a in assignments:
        print(a["name"], a["todoist_task_id"])


def update_notion_page_properties(page_id, properties):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    response = requests.patch(url, headers=headers, json={"properties": properties})
    if response.status_code == 200:
        print("Notion page updated successfully.")
    else:
        print("Failed to update Notion page: ", response.text)