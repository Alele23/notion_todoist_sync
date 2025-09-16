import os
import requests
from dotenv import load_dotenv
from datetime import datetime

from notion import update_notion_page_properties

load_dotenv()

# Gets a list of assignments from Notion
def get_notion_assignments():
    from notion import get_assignments as notion_get_assignments
    return notion_get_assignments()

# Gets a list of assignment names from Notion
def get_notion_names():
    from notion import get_assignment_names
    return get_assignment_names()

# Gets a list of assignments from Todoist
def get_todoist_assignments():
    from todoist import get_assignments
    return get_assignments()

# Gets a list of assignment names from Todoist
def get_todoist_names():
    from todoist import get_assignment_names as todoist_get_assignment_names
    return todoist_get_assignment_names()

# Creates a task in Todoist
def create_todoist_task(assignment):
    from todoist import TodoistAPI, TODOIST_API_KEY, TODOIST_PROJECT_ID, TODOIST_SECTION_ID
    todoist = TodoistAPI(TODOIST_API_KEY)
    due_date_obj = datetime.strptime(assignment['due_date'], '%Y-%m-%d').date()
    course = [assignment["course"]]
    todoist.add_task(content=assignment['name'],
                     project_id=TODOIST_PROJECT_ID,
                     section_id=TODOIST_SECTION_ID,
                     due_date=due_date_obj,
                     labels=course,
                     description=assignment['type'])
    print(f"Task created in Todoist: {assignment['name']}")

# Syncs assignments from Notion to Todoist
def notion_to_todoist():
    from todoist import mark_task_completed
    notion_assignments = get_notion_assignments()

    for assignment in notion_assignments:
        if assignment["todoist_task_id"]:
            if assignment['progress'] == "Completed":
                mark_task_completed(assignment['todoist_task_id'])

        else:
            if assignment['name'] not in get_todoist_names():
                print(f"Adding to Todoist: {assignment}")
                create_todoist_task(assignment)

# Creates an assignment in Notion
def notion_create_assignment(assignment):
    from notion import NOTION_DATABASE_ID, requests, headers
    due_date = assignment['due_date'].isoformat()
    create_url = "https://api.notion.com/v1/pages"

    assignment_properties = {
        "parent": { "database_id": NOTION_DATABASE_ID },
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": assignment['name']
                        }
                    }
                ]
            },
            "due date": {
                "date": {
                    "start": due_date
                }
            },
            "course": {
                "multi_select": [
                    { "name": assignment['course'][0] }
                ]
            },
            "type": {
                "multi_select": [
                    { "name": assignment['type'] }
                ]
            }
        }
    }
    
    # Create a new page in Notion
    new_assignment = requests.post(create_url, headers=headers, json=assignment_properties)
    if new_assignment.status_code == 200:
        print(f"Assignment created in Notion: {assignment['name']}")
    else:
        print("Failed to create assignment in Notion: ", new_assignment.text)

def todoist_to_notion():
    todoist_assignments = get_todoist_assignments()

    for assignment in todoist_assignments:
        if assignment["notion_id"]:  # already linked
            if assignment["completed"]:
                update_notion_page_properties(
                    assignment["notion_id"],
                    {"Progress": {"status": {"name": "Completed"}}}
                )
        else:
            if not assignment["completed"]:  # only sync active tasks
                notion_create_assignment(assignment)

todoist_to_notion()