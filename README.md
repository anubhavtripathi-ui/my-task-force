# My Task Force

Python + Streamlit + Supabase personal task manager.

## Files
- `app.py` - main application
- `requirements.txt` - Python dependencies
- `supabase_schema.sql` - database table + policies

## 1. Create Supabase project
Create a Supabase project and open SQL Editor.
Paste and run `supabase_schema.sql`.

Then copy:
- Project URL
- anon/public API key

## 2. Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 3. Streamlit Cloud
Push these files to GitHub and create a Streamlit app pointing to `app.py`.

In Streamlit Cloud > Settings > Secrets:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"
APP_PIN = "1234"
```

Change `APP_PIN` to your own 4-digit PIN.

## Important
This V1 uses a simple app PIN. The Supabase table policies are intentionally permissive for a single-user prototype. For a public multi-user product, replace them with proper Supabase Auth and user-level Row Level Security.

Snooze currently moves a task one hour forward. Browser/OS push notifications are not implemented in V1.
