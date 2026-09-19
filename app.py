import os
from datetime import datetime, date, time, timedelta
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
    is_glass = st.session_state.theme == "Glass Gradient"
    app_bg = (
        "radial-gradient(circle at 12% 8%, rgba(182,108,255,.28), transparent 30%), "
        "radial-gradient(circle at 88% 12%, rgba(67,221,255,.20), transparent 28%), "
        "linear-gradient(135deg, #151126 0%, #101b35 52%, #17112b 100%)"
        if is_glass else
        "radial-gradient(circle at 10% 0%, rgba(124,92,255,.16), transparent 26%), "
        "radial-gradient(circle at 90% 8%, rgba(0,212,255,.10), transparent 24%), "
        "var(--bg)"
    )
    panel_effect = "backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);" if is_glass else ""
    st.markdown(f"""
    <style>
    :root {{
      --bg:{t["bg"]}; --panel:{t["panel"]}; --card:{t["card"]};
      --text:{t["text"]}; --muted:{t["muted"]}; --accent:{t["accent"]};
      --accent2:{t["accent2"]}; --danger:{t["danger"]}; --border:{t["border"]};
    }}
    .stApp {{
      background:{app_bg};
      color:var(--text);
    }}
    [data-testid="stHeader"] {{ background:transparent; }}
    [data-testid="stMainBlockContainer"] {{
      max-width: 1450px;
      padding-top: 1rem;
      padding-bottom: 2rem;
      padding-left: 1.5rem;
      padding-right: 1.5rem;
    }}
    [data-testid="stSidebar"] {{ background:var(--panel); {panel_effect} }}
    h1,h2,h3,h4 {{ color:var(--text) !important; }}
    p, label, [data-testid="stMarkdownContainer"] {{ color:var(--text); }}
    .hero {{
      padding:14px 18px;
      border:1px solid var(--border);
      border-radius:18px;
      background:linear-gradient(135deg, rgba(124,92,255,.20), rgba(0,212,255,.08));
      margin-bottom:12px;
      {panel_effect}
    }}
    .hero-title {{ font-size:28px; line-height:1.1; font-weight:800; letter-spacing:-.7px; }}
    .hero-sub {{ color:var(--muted) !important; margin-top:3px; font-size:13px; }}
    .metric {{
      border:1px solid var(--border);
      border-radius:14px;
      padding:12px 14px;
      background:var(--card);
      min-height:78px;
      {panel_effect}
    }}
    .metric-num {{ font-size:23px; line-height:1.05; font-weight:800; color:var(--text); }}
    .metric-label {{ color:var(--muted) !important; font-size:12px; margin-top:4px; }}
    .task-card {{
      border:1px solid var(--border);
      border-radius:15px;
      padding:12px 14px;
      background:var(--card);
      margin:7px 0;
      box-shadow:0 6px 18px rgba(0,0,0,.08);
      {panel_effect}
    }}
    .task-title {{ font-size:16px; font-weight:750; color:var(--text); margin-top:5px; }}
    .task-desc {{ color:var(--muted) !important; font-size:13px; margin-top:4px; }}
    .task-meta {{ color:var(--muted) !important; font-size:11px; margin-top:7px; }}
    .urgent {{
      border-color:rgba(255,92,138,.65);
      box-shadow:0 0 0 1px rgba(255,92,138,.08), 0 7px 22px rgba(255,92,138,.08);
    }}
    .done .task-title {{ text-decoration:line-through; opacity:.65; }}
    .chip {{
      display:inline-block;
      padding:3px 8px;
      border-radius:999px;
      background:rgba(124,92,255,.16);
      color:var(--text);
      font-size:10px;
      border:1px solid var(--border);
      margin-right:4px;
    }}
    .urgent-chip {{ background:rgba(255,92,138,.16); }}
    .section-title {{ font-size:19px; font-weight:800; margin:12px 0 6px; color:var(--text); }}
    .small-muted {{ color:var(--muted) !important; font-size:12px; }}

    /* Make native Streamlit controls readable in every theme. */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"],
    textarea,
    input {{
      background:var(--card) !important;
      color:var(--text) !important;
      border-color:var(--border) !important;
    }}
    div[data-baseweb="select"] *,
    div[data-baseweb="input"] *,
    textarea,
    input {{
      color:var(--text) !important;
    }}
    [data-baseweb="popover"] {{
      background:var(--panel) !important;
      color:var(--text) !important;
    }}
    [data-baseweb="popover"] * {{ color:var(--text) !important; }}
    button {{
      color:var(--text) !important;
      border-color:var(--border) !important;
    }}
    button[kind="primary"] {{
      background:var(--accent) !important;
      color:#fff !important;
      border-radius:10px !important;
    }}
    div[role="radiogroup"] {{
      background:var(--panel);
      border:1px solid var(--border);
      border-radius:12px;
      padding:3px 7px;
    }}
    div[role="radiogroup"] label {{ color:var(--text) !important; }}
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
        dt = datetime.combine(due_date, due_time or time(23,59))
        due_at = dt.isoformat()
    data = {
        "title": title.strip(),
        "category": category,
        "priority": priority,
        "description": description.strip()[:300],
        "due_at": due_at,
        "status": "todo",
    }
    supabase.table("tasks").insert(data).execute()

def update_task(task_id, **fields):
    if not supabase:
        db_error_message(); return
    supabase.table("tasks").update(fields).eq("id", task_id).execute()

def delete_task(task_id):
    if not supabase:
        db_error_message(); return
    supabase.table("tasks").delete().eq("id", task_id).execute()

tasks = load_tasks()

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
    theme = st.selectbox("Theme", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme), key="theme_selector")
    if theme != st.session_state.theme:
        st.session_state.theme = theme
        st.rerun()

# ---------- Navigation ----------
pages = ["Dashboard", "Home", "Office", "Outside", "Personal Goals", "Urgent", "Upcoming", "Completed"]
page = st.segmented_control(
    "Navigation",
    pages,
    default="Dashboard",
    key="page_nav",
    label_visibility="collapsed",
    width="stretch",
)


# ---------- Helpers ----------
def parse_due(task):
    raw = task.get("due_at")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None

def visible_tasks(page_name):
    if page_name in CATEGORIES:
        return [t for t in tasks if t.get("category") == page_name and t.get("status") != "completed"]
    if page_name == "Urgent":
        return [t for t in tasks if t.get("priority") == "urgent" and t.get("status") != "completed"]
    if page_name == "Upcoming":
        now = datetime.now()
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
                update_task(tid, status="completed", completed_at=datetime.now().isoformat())
                st.rerun()
        else:
            if st.button("↩ Restore", key=f"restore_{key_prefix}_{tid}", use_container_width=True):
                update_task(tid, status="todo", completed_at=None)
                st.rerun()
    with b:
        if st.button("⏰ Snooze", key=f"snooze_{key_prefix}_{tid}", use_container_width=True):
            new_due = datetime.now() + timedelta(hours=1)
            update_task(tid, due_at=new_due.isoformat())
            st.rerun()
    with c:
        if st.button("✏ Edit", key=f"edit_{key_prefix}_{tid}", use_container_width=True):
            st.session_state[f"editing_{tid}"] = True
    with d:
        if st.button("🗑 Delete", key=f"del_{key_prefix}_{tid}", use_container_width=True):
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
    upcoming = [t for t in pending if parse_due(t) and parse_due(t) >= datetime.now()]
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
            if st.button(f"Open {cat}", key=f"open_cat_{cat}", use_container_width=True):
                st.session_state["page_nav"] = cat
                st.rerun()


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
