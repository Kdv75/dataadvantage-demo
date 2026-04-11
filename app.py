import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import smtplib
from email.mime.text import MIMEText

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
col1.metric("💰 Revenue", f"${total_revenue:,}")
col2.metric("📉 Spend", f"${total_spend:,}")
col3.metric("📊 ROAS", roas)

# ---------------- CHARTS ----------------

# 1) LINE
st.subheader("📈 Revenue Trend")
rev_time = filtered.groupby("date")["revenue"].sum().reset_index()
fig1 = px.line(rev_time, x="date", y="revenue")
st.plotly_chart(fig1, use_container_width=True)

# 2) BAR
st.subheader("📊 Revenue by Channel")
channel_data = filtered.groupby("channel").agg({
    "revenue": "sum",
    "spend": "sum"
}).reset_index()
channel_data["ROAS"] = channel_data["revenue"] / channel_data["spend"]

fig2 = px.bar(
    channel_data,
    x="channel",
    y="revenue",
    color="channel",
    hover_data=["ROAS", "spend"]
)
st.plotly_chart(fig2, use_container_width=True)

# 3) PIE (большой, с %)
st.subheader("🥧 Channel Contribution")
fig3 = px.pie(
    channel_data,
    names="channel",
    values="revenue",
)
fig3.update_traces(textinfo="percent+label")
fig3.update_layout(height=500)
st.plotly_chart(fig3, use_container_width=True)

# ---------------- INSIGHT ----------------
top = channel_data.sort_values("revenue", ascending=False).iloc[0]
st.success(
    f"💡 {top['channel']} drives the most revenue: "
    f"${top['revenue']:,} | ROAS {round(top['ROAS'], 2)}"
)

# ---------------- CTA ----------------
st.markdown("---")

st.subheader("📩 Get your custom dashboard")

st.markdown("""
✔ All marketing data in one place  
✔ Automated reporting (no Excel)  
✔ Clear ROI by channel  
✔ Setup in 7 days  
""")

st.link_button(
    "🚀 Get my dashboard",
    "https://mail.google.com/mail/?view=cm&fs=1&to=info@dataadvantage.io&su=Dashboard%20Request"
)


