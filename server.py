import base64
import hmac
import hashlib
import os
import threading
from fastapi import BackgroundTasks, FastAPI, Request, HTTPException
from dotenv import load_dotenv

load_dotenv()

TODOIST_CLIENT_SECRET = os.getenv("TODOIST_CLIENT_SECRET")
NOTION_VERIFICATION_TOKEN = os.getenv("NOTION_VERIFICATION_TOKEN")

app = FastAPI()

_sync_lock = threading.Lock()
_sync_pending = threading.Event()


def run_sync():
    # Notion pauses webhooks that respond slowly, so sync runs after the response.
    # Events arriving mid-sync collapse into a single follow-up run.
    from sync import sync_assignments
    _sync_pending.set()
    # Re-check after releasing: an event that lost the lock race must not be dropped.
    while _sync_pending.is_set() and _sync_lock.acquire(blocking=False):
        try:
            while _sync_pending.is_set():
                _sync_pending.clear()
                try:
                    sync_assignments()
                except Exception as e:
                    print(f"Sync failed: {e!r}")
        finally:
            _sync_lock.release()


def verify_todoist_signature(body: bytes, signature: str) -> bool:
    expected = base64.b64encode(
        hmac.new(
            TODOIST_CLIENT_SECRET.encode(),
            body,
            hashlib.sha256
        ).digest()
    ).decode()
    return hmac.compare_digest(expected, signature)


@app.post("/webhook/notion")
async def notion_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()

    # Notion sends verification token on first setup
    if "verification_token" in payload:
        if payload["verification_token"] != NOTION_VERIFICATION_TOKEN:
            raise HTTPException(status_code=401, detail="Invalid verification token")
        return {"status": "ok"}

    event_type = payload.get("type")
    print(f"Notion event received: {event_type}")

    if event_type in ("page.properties_updated", "page.created"):
        background_tasks.add_task(run_sync)

    return {"status": "ok"}


@app.post("/webhook/todoist")
async def todoist_webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()

    # Verify the request came from Todoist
    signature = request.headers.get("X-Todoist-Hmac-SHA256")
    if not signature or not verify_todoist_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event_type = payload.get("event_name")
    print(f"Todoist event received: {event_type}")

    if event_type in ("item:completed", "item:updated", "item:added"):
        background_tasks.add_task(run_sync)

    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok"}
