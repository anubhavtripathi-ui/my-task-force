import os
from datetime import datetime, timedelta, timezone

import requests

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
NTFY_TOPIC = os.environ["NTFY_TOPIC"].strip()

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Accept": "application/json",
}

IST = timezone(timedelta(hours=5, minutes=30))
now = datetime.now(timezone.utc)
window_end = now + timedelta(days=3)

params = {
    "select": "id,title,due_at,status",
    "status": "eq.todo",
    "due_at": f"gte.{now.isoformat()}",
    "due_at": f"gte.{now.isoformat()}",
}

# Supabase/PostgREST query parameters cannot contain the same key twice,
# so construct the URL explicitly for the upper bound.
url = (
    f"{SUPABASE_URL}/rest/v1/tasks"
    f"?select=id,title,due_at,status"
    f"&status=eq.todo"
    f"&due_at=gte.{now.isoformat()}"
    f"&due_at=lt.{window_end.isoformat()}"
)

response = requests.get(url, headers=HEADERS, timeout=20)
response.raise_for_status()
tasks = response.json()

for task in tasks:
    due_raw = task.get("due_at")
    if not due_raw:
        continue

    due = datetime.fromisoformat(due_raw.replace("Z", "+00:00"))
    if due.tzinfo is None:
        due = due.replace(tzinfo=IST)

    reminder_at = due - timedelta(minutes=15)

    # If the reminder time has arrived, the app itself handles immediate
    # reminders for newly-created tasks. The scheduler handles future ones.
    if reminder_at <= now:
        continue

    # Re-publishing with the same sequence ID replaces the existing
    # scheduled reminder, so this is safe to run every 5 minutes.
    ntfy_url = f"https://ntfy.sh/{NTFY_TOPIC}/task-{task['id']}"
    ntfy_headers = {
        "At": str(int(reminder_at.timestamp())),
        "Title": "⚡ My Task Force reminder",
        "Priority": "4",
    }
    message = (
        f"{task.get('title', 'Task')} — due "
        f"{due.astimezone(IST).strftime('%d %b, %I:%M %p')}"
    )
    r = requests.post(
        ntfy_url,
        data=message.encode("utf-8"),
        headers=ntfy_headers,
        timeout=20,
    )
    r.raise_for_status()
