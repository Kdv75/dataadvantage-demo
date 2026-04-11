import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import numpy as np
import plotly.express as px
import smtplib
import requests
from email.mime.text import MIMEText

TELEGRAM_TOKEN = "8783134651:AAFqjsD5jM9olIgtmJxxGSSd7XpiU-218Bs"
CHAT_ID = "1799500747"

def send_to_telegram(name, email, company, message):
    text = f"""
🚀 New Lead!

👤 Name: {name}
📧 Email: {email}
🏢 Company: {company}

💬 Request:
{message}
"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }

    requests.post(url, data=payload)

# ---------------- CONFIG ----------------
st.set_page_config(page_title="DataAdvantage Demo", layout="wide")

# ---------------- EMAIL (GoDaddy SMTP) ----------------
def send_email(name, email, company):
    sender = "info@dataadvantage.io"
    receiver = "info@dataadvantage.io"

    # ⚠️ ЛОКАЛЬНО можешь временно вставить пароль строкой.
    # ДЛЯ ДЕПЛОЯ используй st.secrets["EMAIL_PASSWORD"] (см. ниже)
    password = st.secrets.get("EMAIL_PASSWORD", "")

    message = f"""
New lead from DataAdvantage dashboard:

Name: {name}
Email: {email}
Company: {company}
"""

    msg = MIMEText(message)
    msg["Subject"] = "🚀 New Lead from Dashboard"
    msg["From"] = sender
    msg["To"] = receiver

    try:
        # GoDaddy SMTP (основной вариант)
        server = smtplib.SMTP_SSL("smtpout.secureserver.net", 465)
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        return True
    except Exception:
        # Альтернатива (если SSL не зашёл)
        try:
            server = smtplib.SMTP("smtpout.secureserver.net", 587)
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            st.error(f"Email error: {e}")
            return False

# ---------------- HEADER ----------------
st.title("Know exactly where your revenue comes from")
st.caption("Marketing analytics system for SMBs — no Excel, no guesswork")

st.markdown("""
### What you get:
- 📊 Real-time revenue tracking  
- ⚡ Automated reporting  
- 🎯 Channel performance insights  
- 🚫 No more Excel chaos  
""")

# ---------------- DATA (demo) ----------------
np.random.seed(42)
dates = pd.date_range(start="2024-01-01", periods=180)

channels = ["Google Ads", "Facebook", "Organic", "Email"]

data = pd.DataFrame({
    "date": np.random.choice(dates, 1200),
    "channel": np.random.choice(channels, 1200),
    "revenue": np.random.randint(150, 1200, 1200),
    "spend": np.random.randint(50, 500, 1200),
})

data["roas"] = data["revenue"] / data["spend"]

# ---------------- SIDEBAR ----------------
st.sidebar.header("Filters")

selected_channels = st.sidebar.multiselect(
    "Channel",
    options=channels,
    default=channels
)

date_range = st.sidebar.date_input(
    "Date range",
    [data["date"].min(), data["date"].max()]
)

filtered = data[
    (data["channel"].isin(selected_channels)) &
    (data["date"] >= pd.to_datetime(date_range[0])) &
    (data["date"] <= pd.to_datetime(date_range[1]))
]

# ---------------- KPI ----------------
total_revenue = int(filtered["revenue"].sum())
total_spend = int(filtered["spend"].sum())
roas = round(total_revenue / total_spend, 2) if total_spend > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Revenue", f"${total_revenue:,.0f}")
col2.metric("Spend", f"${total_spend:,.0f}")
col3.metric("ROAS", f"{roas:.2f}")

# -------------------- CHARTS --------------------

# 1) LINE
st.subheader("📈 Revenue Trend")

rev_time = filtered.groupby("date")["revenue"].sum().reset_index()

fig1 = px.line(
    rev_time,
    x="date",
    y="revenue"
)

st.plotly_chart(fig1, use_container_width=True)


# 2) DATA FOR CHANNELS
channel_data = filtered.groupby("channel").agg({
    "revenue": "sum",
    "spend": "sum"
}).reset_index()

channel_data["ROAS"] = channel_data["revenue"] / channel_data["spend"]


# 3) BAR
fig2 = px.bar(
    channel_data,
    x="channel",
    y="revenue",
    color="channel",
    hover_data=["ROAS", "spend"]
)


# 4) PIE
fig3 = px.pie(
    channel_data,
    names="channel",
    values="revenue"
)

fig3.update_traces(textinfo="percent+label")
fig3.update_layout(height=500)


# 5) SIDE-BY-SIDE LAYOUT (🔥 главное)
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Revenue by Channel")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("🥧 Channel Contribution")
    st.plotly_chart(fig3, use_container_width=True)


# --------------- INSIGHT ---------------
top = channel_data.sort_values("revenue", ascending=False).iloc[0]

top_channel = top['channel']
revenue = top['revenue']
roas_value = round(top['ROAS'], 2)

st.markdown(f"""
## 🧠 Key Insight

**{top_channel}** is your top-performing channel.

### Why it matters:
- Generates **${revenue:,.0f} revenue**
- Delivers **{roas_value}x return on ad spend**

### Recommended action:
👉 Increase budget allocation to **{top_channel}** to scale growth
""")

# ---------------- CTA ----------------
st.markdown("---")
st.subheader("📩 Start your analytics setup")

with st.form("lead_form"):
    name = st.text_input("Your name")
    email = st.text_input("Email")
    company = st.text_input("Company / Website")
    message = st.text_area("What do you want?")

    submitted = st.form_submit_button("🚀 Get started")
    if submitted:
        if email:
            send_to_telegram(name, email, company, message)  # 👈 ВОТ ЭТО КЛЮЧЕВОЕ
            st.success("✅ Request sent! We'll contact you soon.")
        else:
            st.error("Please enter your email")


