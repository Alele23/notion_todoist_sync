import hmac
import hashlib
import os
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv

load_dotenv()

TODOIST_CLIENT_SECRET = os.getenv("TODOIST_CLIENT_SECRET")

app = FastAPI()


def verify_todoist_signature(body: bytes, signature: str) -> bool:
    expected = hmac.new(
        TODOIST_CLIENT_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@app.post("/webhook/notion")
async def notion_webhook(request: Request):
    payload = await request.json()

    # Notion sends a verification challenge on first setup
    if "challenge" in payload:
        return {"challenge": payload["challenge"]}

    event_type = payload.get("type")
    print(f"Notion event received: {event_type}")

    # Any page change in the database — run notion → todoist sync
    if event_type in ("page.updated", "page.created"):
        from sync import notion_to_todoist
        notion_to_todoist()

    return {"status": "ok"}


@app.post("/webhook/todoist")
async def todoist_webhook(request: Request):
    body = await request.body()

    # Verify the request came from Todoist
    signature = request.headers.get("X-Todoist-Hmac-SHA256")
    if not signature or not verify_todoist_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event_type = payload.get("event_name")
    print(f"Todoist event received: {event_type}")

    # Task completed or updated — run todoist → notion sync
    if event_type in ("item:completed", "item:updated", "item:added"):
        from sync import todoist_to_notion
        todoist_to_notion()

    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"status": "ok"}
