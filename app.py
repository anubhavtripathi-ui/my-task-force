import os
from datetime import datetime, date, time, timedelta, timezone
from zoneinfo import ZoneInfo
import requests
import streamlit as st
from supabase import create_client, Client

# =========================
# My Task Force - V1
# =========================
# For GitHub/Streamlit Cloud:
# Add these in Streamlit Cloud > Settings > Secrets
#
# SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
# SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"
# APP_PIN = "1234"
#
# If you do not configure Supabase yet, the app shows setup instructions.

st.set_page_config(
    page_title="My Task Force",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Config ----------
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
APP_PIN = str(st.secrets.get("APP_PIN", os.getenv("APP_PIN", "1234")))
NTFY_TOPIC = str(st.secrets.get("NTFY_TOPIC", os.getenv("NTFY_TOPIC", ""))).strip()
IST = ZoneInfo("Asia/Kolkata")

CATEGORIES = {
    "Home": "🏠",
    "Office": "💼",
    "Outside": "🚗",
    "Personal Goals": "🎯",
}
THEMES = {
    "Dark Neon": {
        "bg": "#0b1020", "panel": "#121a2f", "card": "#17213a",
        "text": "#f5f7ff", "muted": "#9aa6c2", "accent": "#7c5cff",
        "accent2": "#00d4ff", "danger": "#ff5c8a", "border": "#273454"
    },
    "Modern Light": {
        "bg": "#f4f7fb", "panel": "#ffffff", "card": "#ffffff",
        "text": "#162033", "muted": "#68748a", "accent": "#635bff",
        "accent2": "#00a8cc", "danger": "#e5486d", "border": "#dfe5ef"
    },
    "Glass Gradient": {
        "bg": "#111124", "panel": "rgba(255,255,255,.08)", "card": "rgba(255,255,255,.10)",
        "text": "#ffffff", "muted": "#b7b8d6", "accent": "#b06cff",
        "accent2": "#37e5ff", "danger": "#ff6f9d", "border": "rgba(255,255,255,.15)"
    },
}

if "theme" not in st.session_state:
    st.session_state.theme = "Dark Neon"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ---------- CSS ----------
def inject_css():
    t = THEMES[st.session_state.theme]
    glass = st.session_state.theme == "Glass Gradient"
    dark = st.session_state.theme == "Dark Neon"

    if glass:
        app_bg = "linear-gradient(135deg,#111425 0%,#17152d 45%,#10263a 100%)"
        surface = "rgba(255,255,255,.075)"
        control_bg = "#f7f8fb"
        control_text = "#182033"
        border = "rgba(255,255,255,.18)"
    elif dark:
        app_bg = "#080d18"
        surface = "#111827"
        control_bg = "#f5f7fa"
        control_text = "#172033"
        border = "#2b3852"
    else:
        app_bg = "#f5f7fb"
        surface = "#ffffff"
        control_bg = "#ffffff"
        control_text = "#172033"
        border = "#d9e0ea"

    st.markdown(f"""
    <style>
    :root {{
      --bg:{app_bg}; --surface:{surface}; --card:{t["card"]};
      --text:{t["text"]}; --muted:{t["muted"]}; --accent:{t["accent"]};
      --accent2:{t["accent2"]}; --danger:{t["danger"]};
      --border:{border}; --control-bg:{control_bg}; --control-text:{control_text};
    }}

    .stApp {{
      background:var(--bg) !important;
      color:var(--text) !important;
    }}

    [data-testid="stMainBlockContainer"] {{
      max-width:1380px !important;
      padding-top:.8rem !important;
      padding-bottom:1.5rem !important;
      padding-left:1.2rem !important;
      padding-right:1.2rem !important;
    }}

    [data-testid="stHeader"] {{ background:transparent !important; }}

    h1,h2,h3,h4,h5,p,span,label,
    [data-testid="stMarkdownContainer"] {{
      color:var(--text) !important;
    }}

    /* Header */
    .hero {{
      padding:15px 19px !important;
      border:1px solid var(--border) !important;
      border-radius:15px !important;
      background:linear-gradient(110deg,rgba(99,91,255,.18),rgba(0,168,204,.07)) !important;
      margin-bottom:9px !important;
    }}
    .hero-title {{
      font-size:26px !important;
      line-height:1.1 !important;
      font-weight:800 !important;
      letter-spacing:-.5px !important;
    }}
    .hero-sub {{
      color:var(--muted) !important;
      margin-top:3px !important;
      font-size:12px !important;
    }}

    /* Navigation */
    div[role="radiogroup"] {{
      display:flex !important;
      flex-wrap:nowrap !important;
      gap:2px !important;
      width:100% !important;
      padding:3px !important;
      margin:2px 0 10px !important;
      border:1px solid var(--border) !important;
      border-radius:11px !important;
      background:var(--surface) !important;
    }}
    div[role="radiogroup"] > label {{
      flex:1 1 0 !important;
      justify-content:center !important;
      min-height:32px !important;
      padding:4px 7px !important;
      border-radius:8px !important;
      color:var(--text) !important;
      background:transparent !important;
      font-size:11px !important;
      font-weight:650 !important;
      cursor:pointer !important;
    }}
    div[role="radiogroup"] > label:hover {{
      background:rgba(99,91,255,.13) !important;
    }}
    div[role="radiogroup"] > label:has(input:checked) {{
      background:var(--accent) !important;
      color:#fff !important;
    }}
    div[role="radiogroup"] > label:has(input:checked) * {{
      color:#fff !important;
    }}
    div[role="radiogroup"] > label > div:first-child {{
      display:none !important;
    }}

    /* Theme selector and all inputs */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"],
    textarea,
    input {{
      background:var(--control-bg) !important;
      color:var(--control-text) !important;
      border:1px solid #cbd3df !important;
      border-radius:9px !important;
    }}
    div[data-baseweb="select"] *,
    div[data-baseweb="input"] *,
    textarea,
    input {{
      color:var(--control-text) !important;
    }}
    textarea::placeholder,
    input::placeholder {{
      color:#7a8597 !important;
      opacity:1 !important;
    }}

    /* Date/time controls: force readable text even in dark browser/OS modes. */
    /* Streamlit date/time controls can render the visible value as nested
       segmented elements rather than a plain input. Force the foreground
       on the entire widget tree so Dark Neon and Glass remain readable. */
    [data-testid="stDateInput"],
    [data-testid="stTimeInput"] {{
      color:var(--control-text) !important;
      opacity:1 !important;
    }}
    [data-testid="stDateInput"] *,
    [data-testid="stTimeInput"] * {{
      color:var(--control-text) !important;
      -webkit-text-fill-color:var(--control-text) !important;
      opacity:1 !important;
    }}
    [data-testid="stDateInput"] input,
    [data-testid="stTimeInput"] input,
    [data-testid="stDateInput"] [data-baseweb="input"],
    [data-testid="stTimeInput"] [data-baseweb="input"] {{
      background:var(--control-bg) !important;
      color:var(--control-text) !important;
      -webkit-text-fill-color:var(--control-text) !important;
      color-scheme:light !important;
      opacity:1 !important;
      border:1px solid #cbd3df !important;
    }}
    [data-testid="stDateInput"] svg,
    [data-testid="stTimeInput"] svg {{
      color:var(--control-text) !important;
      fill:var(--control-text) !important;
      opacity:1 !important;
    }}

    [data-baseweb="popover"] {{
      background:#ffffff !important;
      color:#172033 !important;
      border:1px solid #d7dee8 !important;
    }}
    [data-baseweb="popover"] * {{
      color:#172033 !important;
    }}

    /* In-app notifications */
    .notification-bar {{
      display:flex !important;
      justify-content:space-between !important;
      align-items:center !important;
      gap:12px !important;
      padding:9px 12px !important;
      margin:0 0 8px !important;
      border:1px solid rgba(255,193,7,.45) !important;
      border-radius:10px !important;
      background:rgba(255,193,7,.10) !important;
      color:var(--text) !important;
      font-size:12px !important;
    }}
    .notification-bar.quiet {{
      border-color:var(--border) !important;
      background:var(--surface) !important;
      color:var(--muted) !important;
    }}
    .notification-bar span {{ color:var(--muted) !important; }}

    /* Section / metrics */
    .section-title {{
      font-size:18px !important;
      font-weight:750 !important;
      margin:11px 0 6px !important;
      color:var(--text) !important;
    }}
    .metric {{
      border:1px solid var(--border) !important;
      border-radius:12px !important;
      padding:10px 12px !important;
      background:var(--surface) !important;
      min-height:68px !important;
    }}
    .metric-num {{
      font-size:21px !important;
      line-height:1.05 !important;
      font-weight:800 !important;
    }}
    .metric-label {{
      color:var(--muted) !important;
      font-size:11px !important;
      margin-top:3px !important;
    }}

    /* Tasks */
    .task-card {{
      border:1px solid var(--border) !important;
      border-radius:13px !important;
      padding:11px 13px !important;
      background:var(--surface) !important;
      margin:5px 0 !important;
      box-shadow:0 4px 14px rgba(0,0,0,.07) !important;
    }}
    .task-title {{
      font-size:15px !important;
      font-weight:700 !important;
      color:var(--text) !important;
      margin-top:5px !important;
    }}
    .task-desc {{
      color:var(--muted) !important;
      font-size:12px !important;
      margin-top:3px !important;
    }}
    .task-meta {{
      color:var(--muted) !important;
      font-size:10px !important;
      margin-top:6px !important;
    }}
    .urgent {{
      border-color:rgba(255,92,138,.65) !important;
    }}
    .chip {{
      display:inline-block !important;
      padding:3px 7px !important;
      border-radius:999px !important;
      background:rgba(99,91,255,.14) !important;
      color:var(--text) !important;
      font-size:9px !important;
      border:1px solid var(--border) !important;
    }}

    /* Buttons */
    .stButton > button {{
      min-height:34px !important;
      padding:5px 9px !important;
      border-radius:8px !important;
      border:1px solid var(--border) !important;
      background:var(--surface) !important;
      color:var(--text) !important;
      font-size:11px !important;
      font-weight:650 !important;
    }}
    .stButton > button:hover {{
      border-color:var(--accent) !important;
      color:var(--text) !important;
    }}
    .stButton > button[kind="primary"] {{
      background:var(--accent) !important;
      color:#fff !important;
      border-color:var(--accent) !important;
    }}

    /* Add-task panel */
    [data-testid="stExpander"] {{
      border:1px solid var(--border) !important;
      border-radius:11px !important;
      background:var(--surface) !important;
      margin-bottom:8px !important;
    }}
    [data-testid="stExpander"] summary {{
      color:var(--text) !important;
      font-size:13px !important;
      font-weight:650 !important;
    }}
    [data-testid="stCaptionContainer"] p {{
      color:var(--muted) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

inject_css()

# ---------- Login ----------
if not st.session_state.authenticated:
    st.markdown("""
    <div class="hero">
      <div class="hero-title">⚡ My Task Force</div>
      <div class="hero-sub">Your personal command center for everyday tasks.</div>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        pin = st.text_input("4-digit PIN", type="password", max_chars=4, placeholder="••••")
        if st.button("Unlock", type="primary", use_container_width=True):
            if pin == APP_PIN:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect PIN.")
        st.caption("PIN is configured in Streamlit Secrets as APP_PIN.")
    st.stop()

# ---------- Supabase ----------
@st.cache_resource
def get_supabase() -> Client | None:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

def local_now():
    return datetime.now(IST)

def schedule_reminder(task_id, title, due_at):
    """Schedule a phone/desktop push reminder through ntfy, if configured."""
    if not NTFY_TOPIC or not due_at:
        return False
    try:
        if due_at.tzinfo is None:
            due_at = due_at.replace(tzinfo=IST)
        reminder_at = due_at - timedelta(minutes=15)
        now = datetime.now(timezone.utc)
        if reminder_at <= datetime.now(IST):
            if due_at > datetime.now(IST):
                headers = {"In": "10s", "Title": "⚡ My Task Force reminder", "Priority": "4"}
            else:
                return False
        else:
            delay_seconds = (reminder_at.astimezone(timezone.utc) - now).total_seconds()
            # ntfy supports delayed delivery for up to 3 days.
            if delay_seconds > 3 * 24 * 60 * 60:
                return False
            headers = {
                "At": str(int(reminder_at.timestamp())),
                "Title": "⚡ My Task Force reminder",
                "Priority": "4",
            }
        url = f"https://ntfy.sh/{NTFY_TOPIC}/task-{task_id}"
        response = requests.post(url, data=f"{title} — due {due_at.astimezone(IST).strftime('%d %b, %I:%M %p')}".encode("utf-8"), headers=headers, timeout=10)
        response.raise_for_status()
        return True
    except Exception:
        return False

def cancel_reminder(task_id):
    if not NTFY_TOPIC:
        return
    try:
        requests.delete(f"https://ntfy.sh/{NTFY_TOPIC}/task-{task_id}", timeout=10)
    except Exception:
        pass

def db_error_message():
    st.error("Supabase is not connected. Add SUPABASE_URL and SUPABASE_KEY in Streamlit Secrets, then reload.")

def load_tasks():
    if not supabase:
        return []
    try:
        r = supabase.table("tasks").select("*").order("created_at", desc=True).execute()
        return r.data or []
    except Exception as e:
        st.error(f"Database error: {e}")
        return []

def add_task(title, category, priority, due_date, due_time, description):
    if not supabase:
        db_error_message(); return
    due_at = None
    if due_date:
        dt = datetime.combine(due_date, due_time or time(23,59)).replace(tzinfo=IST)
        due_at = dt.isoformat()
    data = {
        "title": title.strip(),
        "category": category,
        "priority": priority,
        "description": description.strip()[:300],
        "due_at": due_at,
        "status": "todo",
    }
    result = supabase.table("tasks").insert(data).execute()
    created = (result.data or [None])[0]
    if created:
        schedule_reminder(created.get("id"), created.get("title", title), parse_due(created))

def update_task(task_id, **fields):
    if not supabase:
        db_error_message(); return
    supabase.table("tasks").update(fields).eq("id", task_id).execute()

def delete_task(task_id):
    if not supabase:
        db_error_message(); return
    supabase.table("tasks").delete().eq("id", task_id).execute()

tasks = load_tasks()


# ---------- In-app notifications ----------
def render_notifications():
    pending = [t for t in tasks if t.get("status") != "completed"]
    now = local_now()
    overdue = []
    due_soon = []
    for t in pending:
        due = parse_due(t)
        if not due:
            continue
        if due < now:
            overdue.append((t, due))
        elif due <= now + timedelta(minutes=15):
            due_soon.append((t, due))

    total_alerts = len(overdue) + len(due_soon)
    if total_alerts:
        st.markdown(
            f'<div class="notification-bar"><b>🔔 Notifications ({total_alerts})</b>'
            f'<span> {len(overdue)} overdue · {len(due_soon)} due within 15 min</span></div>',
            unsafe_allow_html=True,
        )

        if overdue:
            st.error(
                "🔴 **Overdue tasks** — " +
                " · ".join(
                    f'**{t.get("title","")}** ({max(1, int((now-due).total_seconds()//60))} min overdue)'
                    for t, due in sorted(overdue, key=lambda x: x[1])
                )
            )

        if due_soon:
            st.warning(
                "🟠 **Due soon** — " +
                " · ".join(
                    f'**{t.get("title","")}** ({max(1, int((due-now).total_seconds()//60))} min)'
                    for t, due in sorted(due_soon, key=lambda x: x[1])
                )
            )
    else:
        st.markdown(
            '<div class="notification-bar quiet"><b>🔔 Notifications</b><span> No active reminders</span></div>',
            unsafe_allow_html=True,
        )

render_notifications()

# ---------- Header ----------
top1, top2 = st.columns([5, 2], vertical_alignment="center")
with top1:
    st.markdown("""
    <div class="hero">
      <div class="hero-title">⚡ My Task Force</div>
      <div class="hero-sub">Plan it. Do it. Tick it off.</div>
    </div>
    """, unsafe_allow_html=True)
with top2:
    theme = st.selectbox("Theme", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme), key="theme_selector", label_visibility="visible")
    if theme != st.session_state.theme:
        st.session_state.theme = theme
        st.rerun()
    if st.button("↻ Check reminders", use_container_width=True):
        st.rerun()

# ---------- Navigation ----------
pages = ["Dashboard", "Home", "Office", "Outside", "Personal Goals", "Urgent", "Upcoming", "Completed"]
page = st.radio(
    "Navigation",
    pages,
    index=0,
    key="page_nav",
    horizontal=True,
    label_visibility="collapsed",
)


# ---------- Helpers ----------
def parse_due(task):
    raw = task.get("due_at")
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=IST)
        return parsed.astimezone(IST)
    except Exception:
        return None

def visible_tasks(page_name):
    if page_name in CATEGORIES:
        return [t for t in tasks if t.get("category") == page_name and t.get("status") != "completed"]
    if page_name == "Urgent":
        return [t for t in tasks if t.get("priority") == "urgent" and t.get("status") != "completed"]
    if page_name == "Upcoming":
        now = local_now()
        return [t for t in tasks if t.get("status") != "completed" and parse_due(t) and parse_due(t) >= now]
    if page_name == "Completed":
        return [t for t in tasks if t.get("status") == "completed"]
    return [t for t in tasks if t.get("status") != "completed"]

def task_card(task, key_prefix):
    tid = task["id"]
    icon = CATEGORIES.get(task.get("category"), "📌")
    priority = task.get("priority") == "urgent"
    due = parse_due(task)
    due_text = due.strftime("%d %b · %I:%M %p") if due else "No due time"
    cls = "task-card urgent" if priority else "task-card"
    if task.get("status") == "completed":
        cls += " done"
    chip = '<span class="chip urgent-chip">⭐ URGENT</span>' if priority else '<span class="chip">NORMAL</span>'
    st.markdown(
        f"""<div class="{cls}">
          <div>{chip}</div>
          <div class="task-title">{icon} {task.get("title","")}</div>
          <div class="task-desc">{(task.get("description") or "").replace("<","&lt;").replace(">","&gt;")}</div>
          <div class="task-meta">{icon} {task.get("category","")} · 📅 {due_text}</div>
        </div>""",
        unsafe_allow_html=True,
    )
    a,b,c,d = st.columns([1,1,1,1])
    with a:
        if task.get("status") != "completed":
            if st.button("✓ Complete", key=f"done_{key_prefix}_{tid}", use_container_width=True):
                update_task(tid, status="completed", completed_at=local_now().isoformat())
                cancel_reminder(tid)
                st.rerun()
        else:
            if st.button("↩ Restore", key=f"restore_{key_prefix}_{tid}", use_container_width=True):
                update_task(tid, status="todo", completed_at=None)
                st.rerun()
    with b:
        if st.button("⏰ Snooze", key=f"snooze_{key_prefix}_{tid}", use_container_width=True):
            new_due = local_now() + timedelta(hours=1)
            update_task(tid, due_at=new_due.isoformat())
            schedule_reminder(tid, task.get("title", ""), new_due)
            st.rerun()
    with c:
        if st.button("✏ Edit", key=f"edit_{key_prefix}_{tid}", use_container_width=True):
            st.session_state[f"editing_{tid}"] = True
    with d:
        if st.button("🗑 Delete", key=f"del_{key_prefix}_{tid}", use_container_width=True):
            cancel_reminder(tid)
            delete_task(tid)
            st.rerun()

    if st.session_state.get(f"editing_{tid}", False):
        with st.form(f"edit_form_{key_prefix}_{tid}"):
            new_title = st.text_input("Task", value=task.get("title",""))
            new_desc = st.text_area("Details", value=task.get("description",""), max_chars=300)
            new_cat = st.selectbox("Category", list(CATEGORIES.keys()), index=list(CATEGORIES.keys()).index(task.get("category","Home")))
            new_pri = st.selectbox("Priority", ["normal","urgent"], index=1 if task.get("priority")=="urgent" else 0)
            if st.form_submit_button("Save changes", type="primary"):
                update_task(tid, title=new_title.strip(), description=new_desc[:300], category=new_cat, priority=new_pri)
                st.session_state[f"editing_{tid}"] = False
                st.rerun()

# ---------- Add task ----------
with st.expander("＋ New Task / 🎤 Speak Task", expanded=False):
    st.caption("Typing is the reliable V1 input. Voice capture/transcription can be added later without changing the database structure.")
    st.caption("🔔 Reminder: 15 minutes before the due time. Phone/desktop notification works even when this app is not open, after NTFY_TOPIC is configured.")
    with st.form("new_task_form", clear_on_submit=True):
        c1,c2 = st.columns([2,1])
        with c1:
            title = st.text_input("Task", placeholder="e.g. Get car serviced")
            description = st.text_area("Details (max 300 characters)", max_chars=300, placeholder="Add 2–3 lines of useful context.")
        with c2:
            category = st.selectbox("Category", list(CATEGORIES.keys()))
            priority = st.selectbox("Priority", ["normal","urgent"])
            due_date = st.date_input("Due date", value=date.today())
            due_time = st.time_input("Due time", value=time(18,0))
        if st.form_submit_button("Save Task", type="primary", use_container_width=True):
            if not title.strip():
                st.error("Enter a task name.")
            elif not supabase:
                db_error_message()
            else:
                add_task(title, category, priority, due_date, due_time, description)
                st.success("Task added.")
                st.rerun()

# ---------- Dashboard ----------
if page == "Dashboard":
    pending = [t for t in tasks if t.get("status") != "completed"]
    completed = [t for t in tasks if t.get("status") == "completed"]
    urgent = [t for t in pending if t.get("priority") == "urgent"]
    upcoming = [t for t in pending if parse_due(t) and parse_due(t) >= local_now()]
    total = len(pending) + len(completed)
    pct = round((len(completed)/total)*100) if total else 0

    st.markdown('<div class="section-title">Today’s Command Center</div>', unsafe_allow_html=True)
    m1,m2,m3,m4 = st.columns(4)
    for col, num, label in [
        (m1, len(pending), "To Do"),
        (m2, len(urgent), "⭐ Urgent"),
        (m3, len(upcoming), "Upcoming"),
        (m4, f"{pct}%", "Completed"),
    ]:
        with col:
            st.markdown(f'<div class="metric"><div class="metric-num">{num}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Quick Access</div>', unsafe_allow_html=True)
    cols = st.columns(4)
    for col, (cat, icon) in zip(cols, CATEGORIES.items()):
        count = len([t for t in pending if t.get("category") == cat])
        with col:
            st.markdown(
                f'<div class="metric"><div class="metric-num">{icon}</div><div class="metric-label">{cat} · {count} pending</div></div>',
                unsafe_allow_html=True
            )

    st.markdown('<div class="section-title">Next Up</div>', unsafe_allow_html=True)
    for i,t in enumerate(sorted(upcoming, key=lambda x: parse_due(x) or datetime.max)[:6]):
        task_card(t, f"dash_{i}")

else:
    heading_icon = CATEGORIES.get(page, {"Urgent":"⭐","Upcoming":"📅","Completed":"✅"}.get(page,"📌"))
    st.markdown(f'<div class="section-title">{heading_icon} {page}</div>', unsafe_allow_html=True)
    selected = visible_tasks(page)
    if not selected:
        st.info("No tasks in this section.")
    else:
        for i,t in enumerate(selected):
            task_card(t, f"{page}_{i}")

# ---------- Logout ----------
st.divider()
c1,c2,c3 = st.columns([1,1,4])
with c1:
    if st.button("Lock App"):
        st.session_state.authenticated = False
        st.rerun()
with c2:
    st.caption(f"{len([t for t in tasks if t.get('status')!='completed'])} pending tasks")
