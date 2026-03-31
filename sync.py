import requests
from dotenv import load_dotenv
from datetime import datetime

from notion import update_notion_page_properties

load_dotenv()

def sync_assignments():
    print("Starting synchronization...")
    notion_to_todoist()
    todoist_to_notion()
    print("Synchronization complete.")

# Gets a list of assignments from Notion
def get_notion_assignments():
    from notion import get_assignments as notion_get_assignments
    return notion_get_assignments()

# Gets a list of assignment names from Notion
def get_notion_names():
    from notion import get_assignment_names
    return get_assignment_names()

# Gets a list of Todoist assignments
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
    task = todoist.add_task(content=assignment['name'],
                            project_id=TODOIST_PROJECT_ID,
                            section_id=TODOIST_SECTION_ID,
                            due_date=due_date_obj,
                            labels=course,
                            description=assignment['type'])
    # Save the Todoist task ID back to Notion so the two are linked
    update_notion_page_properties(assignment['notion_id'], {
        "Todoist Task ID": {
            "rich_text": [{"text": {"content": task.id}}]
        }
    })
    print(f"Task created in Todoist: {assignment['name']}")

# Syncs assignments from Notion to Todoist
def notion_to_todoist():
    from todoist import mark_task_completed
    from notion import get_all_assignments
    all_assignments = get_all_assignments()

    for assignment in all_assignments:
        if assignment["todoist_task_id"]:
            if assignment['progress'] == "Completed":
                mark_task_completed(assignment['todoist_task_id'])
        else:
            if assignment['progress'] != "Completed":
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
    from notion import get_all_assignments
    todoist_assignments = get_todoist_assignments()
    active_todoist_ids = {a['todoist_task_id'] for a in todoist_assignments}

    # Create Notion assignments for Todoist tasks not yet linked to Notion
    for assignment in todoist_assignments:
        if not assignment["notion_id"]:
            if assignment['name'] not in get_notion_names():
                notion_create_assignment(assignment)

    # Mark Notion assignments as completed when their Todoist task is no longer active
    for assignment in get_all_assignments():
        if (assignment["todoist_task_id"]
                and assignment["todoist_task_id"] not in active_todoist_ids
                and assignment['progress'] != "Completed"):
            update_notion_page_properties(
                assignment["notion_id"],
                {"Progress": {"status": {"name": "Completed"}}}
            )
            print(f"Marked as completed in Notion: {assignment['name']}")

sync_assignments()
