# Notion ↔ Todoist Sync

### A bidirectional synchronization tool between a Notion database and a Todoist project.
### Automatically syncs tasks between both platforms, including due dates, labels, and project sections.
### Runs as a local webhook server with real-time sync triggered by Notion and Todoist events.

## ✨ Features

    Bidirectional sync:

    Notion → Todoist: Creates new Todoist tasks from Notion assignments.

    Todoist → Notion: Creates new Notion pages from Todoist tasks.

    Property mapping: Maps task name, due date, course, and type between platforms.

    Project section support: Places Todoist tasks in a specific section (e.g., Upcoming Assignments).

    Real-time automation: Webhook-driven sync via a local FastAPI server exposed through Cloudflare Tunnel.

    Auto-start: launchd keeps the server and tunnel running automatically on login.


## 📦 Requirements

    Python 3.9+

    Notion integration token and database ID

    Todoist API token and project ID (and optional section ID)

    Packages:

    pip install requests python-dotenv notion-client todoist-api-python fastapi uvicorn

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
TODOIST_CLIENT_SECRET=your_todoist_client_secret
NOTION_VERIFICATION_TOKEN=your_notion_verification_token
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
## 🔄 Automation with Webhooks + Cloudflare Tunnel

Sync is triggered in real time by webhooks from Notion and Todoist. A local FastAPI server receives the events and runs the sync logic. Cloudflare Tunnel exposes the server publicly without port forwarding.

### 1. Install cloudflared
```
brew install cloudflare/cloudflare/cloudflared
```

### 2. Create and configure a tunnel
```
cloudflared tunnel login
cloudflared tunnel create notion-todoist-sync
cloudflared tunnel route dns notion-todoist-sync sync.yourdomain.com
```

### 3. Start the server and tunnel
```
uvicorn server:app --port 8000
cloudflared tunnel run notion-todoist-sync
```

### 4. Register webhooks
- **Todoist**: add `https://sync.yourdomain.com/webhook/todoist` in the Todoist developer console
- **Notion**: add `https://sync.yourdomain.com/webhook/notion` via your Notion integration settings

### 5. Auto-start on login (macOS)

Copy the plist files from `launchd/` to `~/Library/LaunchAgents/`, then load them:
```
launchctl load ~/Library/LaunchAgents/com.adamlele.notionsync.plist
launchctl load ~/Library/LaunchAgents/com.adamlele.cloudflared.plist
```

### 6. Check logs
```
tail -f server.log
tail -f cloudflared.log
```
## 📋 Project Structure
```
notion_todoist_sync/
├── notion.py           # Fetch and parse assignments from Notion
├── todoist.py          # Fetch and parse tasks from Todoist
├── sync.py             # Bidirectional sync logic
├── server.py           # FastAPI webhook server
├── launchd/            # macOS launchd plists for auto-start
├── .env                # API keys and configuration
├── requirements.txt
└── README.md
```
