import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Gets a list of assignments from Notion
def get_notion_assignments():
    from notion import get_assignments as notion_get_assignments
    return notion_get_assignments()

# Gets a list of assignment names from Notion
def get_notion_names():
    from notion import get_assignment_names as notion_get_assignment_names
    return notion_get_assignment_names()

# Gets a list of assignments from Todoist
def get_todoist_assignments():
    from todoist import get_assignments as todoist_get_assignments
    return todoist_get_assignments()

# Gets a list of assignment names from Todoist
def get_todoist_names():
    from todoist import get_assignment_names as todoist_get_assignment_names
    return todoist_get_assignment_names()

# Creates a task in Todoist
def create_todoist_task(assignment):
    from todoist import TodoistAPI, TODOIST_API_KEY, TODOIST_PROJECT_ID
    todoist = TodoistAPI(TODOIST_API_KEY)
    due_date_obj = datetime.strptime(assignment['due_date'], '%Y-%m-%d').date()
    course = []
    course.append(assignment['course'])
    todoist.add_task(content=assignment['name'],
                     project_id=TODOIST_PROJECT_ID,
                     due_date=due_date_obj,
                     labels=course,
                     description=assignment['type'])
    print(f"Task created in Todoist: {assignment['name']}")

# Syncs assignments from Notion to Todoist
def notion_to_todoist():
    notion_assignments = get_notion_assignments()
    todoist_assignment_names = get_todoist_names()

    for assignment in notion_assignments:
        if assignment['name'] not in todoist_assignment_names:
            print(f"Adding to Todoist: {assignment}")
            create_todoist_task(assignment)

notion_to_todoist()