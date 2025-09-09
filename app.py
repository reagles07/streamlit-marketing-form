import streamlit as st
from datetime import date, timedelta
import time, re, csv
from pathlib import Path
from io import StringIO

# ---------- Page setup ----------
st.set_page_config(page_title="Marketing Request Form", page_icon="📝", layout="centered")
st.title("📝 Marketing Request Form")
st.caption("Submit a marketing request and we’ll get back to you shortly.")

# ---------- Helpers ----------
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
def clean_phone(p: str) -> str:
    return re.sub(r"\D+", "", p or "")

CSV_PATH = Path("requests.csv")

def append_to_csv(payload: dict):
    is_new = not CSV_PATH.exists()
    with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow([
                "timestamp","name","email","phone","channel",
                "activity","notes","start_date","end_date"
            ])
        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"),
            payload["name"], payload["email"], payload["phone"],
            payload["channel"], payload["activity"], payload["notes"],
            payload["start_date"], payload["end_date"]
        ])

def to_csv_row(payload: dict) -> str:
    sio = StringIO()
    writer = csv.writer(sio)
    writer.writerow([
        "timestamp","name","email","phone","channel",
        "activity","notes","start_date","end_date"
    ])
    writer.writerow([
        time.strftime("%Y-%m-%d %H:%M:%S"),
        payload["name"], payload["email"], payload["phone"],
        payload["channel"], payload["activity"], payload["notes"],
        payload["start_date"], payload["end_date"]
    ])
    return sio.getvalue()

# ---------- Form ----------
with st.form("marketing_request"):
    name = st.text_input("Full name *")
    email = st.text_input("Email *")
    phone = st.text_input("Phone *", placeholder="+1 416 555 0123")
    channel = st.selectbox("Channel *", ["retail", "ecommerce", "inline", "kiosk"])

    marketing_activity = st.selectbox(
        "Marketing activity required *",
        [
            "Google Ads",
            "Social Media Campaign",
            "SEO",
            "Email Newsletter",
            "In-store Event",
            "Website Update",
            "Influencer Collaboration",
            "SMS Campaign",
            "OOH/Billboard",
            "Print Flyers"
        ]
    )

    notes = st.text_area(
        "Notes (brief requirements)",
        placeholder="Key goals, target audience, budget range, KPIs, etc.",
        help="A short brief about what you need."
    )

    # Date range selector (duration)
    today = date.today()
    start_end = st.date_input(
        "Expected activity duration * (select start and end dates)",
        value=(today, today + timedelta(days=7))
    )

    submitted = st.form_submit_button("Submit")

# ---------- Submission handling ----------
if submitted:
    # Basic validation
    errors = []
    if not name.strip():
        errors.append("Name is required.")
    if not EMAIL_RE.match(email or ""):
        errors.append("Enter a valid email address.")
    cleaned_phone = clean_phone(phone)
    if len(cleaned_phone) < 7:
        errors.append("Enter a valid phone number (at least 7 digits).")

    if not isinstance(start_end, tuple) or len(start_end) != 2:
        errors.append("Please select a start and an end date for the duration.")
    else:
        start_date, end_date = start_end
        if start_date > end_date:
            errors.append("Start date cannot be after end date.")

    if errors:
        st.error("Please fix the following issues:")
        for e in errors:
            st.markdown(f"- {e}")
        st.stop()

    # Simulated wait times and progress to show UX feedback
    progress = st.progress(0)
    with st.spinner("Submitting your request..."):
        for pct in range(0, 101, 20):
            time.sleep(0.25)   # <-- intentional short wait time
            progress.progress(pct)

    payload = {
        "name": name.strip(),
        "email": email.strip(),
        "phone": cleaned_phone,
        "channel": channel,
        "activity": marketing_activity,
        "notes": (notes or "").strip(),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }

    # Save to CSV
    append_to_csv(payload)
    st.toast("Saved to requests.csv", icon="✅")

    st.success("Thanks! Your request has been submitted. We’ll reach out soon.")
    st.write("If you’d like, you can download your submission as a CSV row:")

    st.download_button(
        label="Download my submission (CSV)",
        data=to_csv_row(payload),
        file_name=f"marketing_request_{int(time.time())}.csv",
        mime="text/csv",
    )

# ---------- Footer ----------
with st.expander("What happens with my data?"):
    st.write(
        "Your submission is stored in a local CSV file named `requests.csv` in the app folder. "
        "If you deploy this, consider moving to a database and securing access."
    )
