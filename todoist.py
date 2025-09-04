import os
from todoist_api_python.api import TodoistAPI
from dotenv import load_dotenv

def print_assignments():
    for assignment in assignments:
        print(f"Name: {assignment['name']}, Due Date: {assignment['due_date']}, Course: {assignment['course']}, Type: {assignment['type']}, Completed: {assignment['completed']}")

def get_assignment_names():
    return [assignment['name'] for assignment in assignments]

def get_assignments():
    return assignments

def mark_task_completed(task_id):
    try:
        todoist.close_task(task_id)
        print(f"Task {task_id} marked as completed.")
    except Exception as e:
        print(f"Error marking task {task_id} as completed: {e}")

load_dotenv()
TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")
TODOIST_PROJECT_ID = os.getenv("TODOIST_PROJECT_ID")
TODOIST_SECTION_ID = os.getenv("TODOIST_SECTION_ID")

# Initialize Todoist client
todoist = TodoistAPI(TODOIST_API_KEY)

assignments = []

# Get tasks from Todoist project and store them in assignments list
tasks = todoist.get_tasks(project_id=TODOIST_PROJECT_ID)
for task in tasks:
    for i in range(len(task)):
        assignment = {
            "name": task[i].content,
            "due_date": task[i].due.date if task[i].due else "No due date",
            "course": task[i].labels,
            "type": task[i].description,
            "completed": task[i].is_completed,
            "todoist_task_id": task[i].id,
            "notion_id": ""
        }
        assignments.append(assignment)
        print(assignment["completed"])

