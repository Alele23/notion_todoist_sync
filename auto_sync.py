import schedule
import time
from sync import notion_to_todoist, todoist_to_notion

def sync():
    print("Starting sync...")
    notion_to_todoist()
    todoist_to_notion()
    print("Sync completed.")

# Schedule the sync function to run every 5 minutes
schedule.every(5).minutes.do(sync)

while True:
    schedule.run_pending()
    time.sleep(1)