from datetime import datetime
from sync import notion_to_todoist, todoist_to_notion

def sync():
    print(f"[{datetime.now()}] Starting sync...")
    notion_to_todoist()
    todoist_to_notion()
    print(f"[{datetime.now()}] Sync completed.")

if __name__ == "__main__":
    sync()