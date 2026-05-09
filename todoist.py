import os
from todoist_api_python.api import TodoistAPI
from dotenv import load_dotenv

load_dotenv()
TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")
TODOIST_PROJECT_ID = os.getenv("TODOIST_PROJECT_ID")
TODOIST_SECTION_ID = os.getenv("TODOIST_SECTION_ID")

todoist = TodoistAPI(TODOIST_API_KEY)

assignments = []


def load():
    global assignments
    assignments = []
    tasks = todoist.get_tasks(project_id=TODOIST_PROJECT_ID)
    for task_list in tasks:
        for task in task_list:
            notion_id = ""
            task_type = task.description or ""
            if task.description and "NotionID:" in task.description:
                parts = task.description.split("\nNotionID:")
                task_type = parts[0]
                notion_id = parts[1].strip() if len(parts) > 1 else ""

            assignments.append({
                "name": task.content,
                "due_date": task.due.date if task.due else "No due date",
                "course": task.labels,
                "type": task_type,
                "completed": task.is_completed,
                "todoist_task_id": task.id,
                "notion_id": notion_id
            })


def get_assignment_names():
    return [assignment['name'] for assignment in assignments]

def get_assignments():
    return assignments

def print_assignments():
    for assignment in assignments:
        print(f"Name: {assignment['name']}, Due Date: {assignment['due_date']}, Course: {assignment['course']}, Type: {assignment['type']}, Completed: {assignment['completed']}")

def mark_task_completed(task_id):
    try:
        todoist.complete_task(task_id)
        print(f"Task {task_id} marked as completed.")
    except Exception as e:
        print(f"Error marking task {task_id} as completed: {e}")
