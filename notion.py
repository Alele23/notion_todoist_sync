import os
import requests
from notion_client import Client
from dotenv import load_dotenv

def get_assignment_names():
    return [assignment["name"] for assignment in assignments]

def get_assignments():
    return assignments

def get_completed_assignments():
    return completed_assignments

def get_all_assignments():
    return assignments + completed_assignments

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

def fetch_all_pages(filter_body, label=""):
    results = []
    body = dict(filter_body)
    while True:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code != 200:
            print(f"Failed to return {label} data from Notion API: ", response.text)
            break
        data = response.json()
        results.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        body["start_cursor"] = data["next_cursor"]
    return results

def parse_page(page):
    properties = page["properties"]
    return {
        "name": properties["Name"]["title"][0]["text"]["content"] if properties["Name"]["title"] else "Untitled",
        "due_date": properties["due date"]["date"]["start"] if properties["due date"]["date"] else "No due date",
        "course": properties["course"]["multi_select"][0]["name"] if properties["course"]["multi_select"] else "No course",
        "type": properties["type"]["multi_select"][0]["name"] if properties["type"]["multi_select"] else "No type",
        "notion_id": page["id"],
        "progress": properties["Progress"]["status"]["name"] if properties["Progress"]["status"] else "No status",
        "todoist_task_id": properties["Todoist Task ID"]["rich_text"][0]["text"]["content"]
            if properties.get("Todoist Task ID") and properties["Todoist Task ID"]["rich_text"] else ""
    }

assignments = [parse_page(page) for page in fetch_all_pages(status_filter, "active")]

completed_filter = {
    "filter": {
        "property": "Progress",
        "status": {
            "equals": "Complete"
        }
    }
}

completed_assignments = [parse_page(page) for page in fetch_all_pages(completed_filter, "completed")]


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

print(get_assignment_names())
