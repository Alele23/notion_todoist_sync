# Notion ↔ Todoist Sync

### A bidirectional synchronization tool between a Notion database and a Todoist project.
### Automatically syncs tasks between both platforms, including due dates, labels, and project sections.
### Runs on a set schedule using cron for continuous background syncing.

## ✨ Features

    Bidirectional sync:

    Notion → Todoist: Creates new Todoist tasks from Notion assignments.

    Todoist → Notion: Creates new Notion pages from Todoist tasks.

    Property mapping: Maps task name, due date, course, and type between platforms.

    Project section support: Places Todoist tasks in a specific section (e.g., Upcoming Assignments).

    Automated schedule: Runs continuously at set intervals via cron.

    Logging: Timestamped logs for each sync run to track execution and runtime.


## 📦 Requirements

    Python 3.9+

    Notion integration token and database ID

    Todoist API token and project ID (and optional section ID)

    Packages:

    pip install requests python-dotenv notion-client todoist-api-python schedule

## ⚙️ Setup
### 1. Clone the repo

```
git clone https://github.com/yourusername/notion-todoist-sync.git
cd notion-todoist-sync
```

### 2. Create a `.env` file

```
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_notion_database_id
TODOIST_API_KEY=your_todoist_api_key
TODOIST_PROJECT_ID=your_todoist_project_id
TODOIST_SECTION_ID=your_todoist_section_id   # optional
```

### 3. Set up a virtual environment
```
python3 -m venv venv
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows
```
### 4. Install dependencies
```
pip install -r requirements.txt
```
### 5. Test manually

Run a one-time sync:
```
python sync.py
```
## 🔄 Automation with `Cron`
### 1. Create auto_sync.py

This file runs the sync once (cron will handle the scheduling):
```
from datetime import datetime
from sync import notion_to_todoist, todoist_to_notion

def sync():
    start = datetime.now()
    print(f"[{start}] Starting sync...")
    notion_to_todoist()
    todoist_to_notion()
    end = datetime.now()
    elapsed = (end - start).total_seconds()
    print(f"[{end}] Sync completed in {elapsed:.2f}s\n{'-'*60}")

if __name__ == "__main__":
    sync()
```
### 2. Edit your crontab
```
crontab -e
```
### Add a job to run every 10 minutes:
```
*/10 * * * * /full/path/to/venv/bin/python /full/path/to/auto_sync.py >> /full/path/to/auto_sync.log 2>&1
```
### 3. Check logs
```
tail -f /full/path/to/auto_sync.log
```
## 📋 Project Structure
```
notion_todoist_sync/
├── notion.py           # Fetch and parse tasks from Notion
├── todoist.py          # Fetch and parse tasks from Todoist
├── sync.py             # Sync logic in both directions
├── auto_sync.py        # Cron-friendly entry point
├── .env                # API keys and configuration
├── requirements.txt
└── README.md
```
