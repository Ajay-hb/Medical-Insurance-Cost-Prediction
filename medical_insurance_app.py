import streamlit as st
import pandas as pd
import joblib
import tempfile
import time

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Medical Insurance Predictor", layout="wide")

model = joblib.load("model.pkl")

# ---------------- PREMIUM CSS ----------------
st.markdown("""
<style>

/* HEADER CONTAINER */
.header-box {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 20px;
    animation: fadeIn 1s ease-in;
}

/* TITLE */
.header-title {
    font-size: 42px;
    font-weight: bold;
    background: linear-gradient(90deg,#00c6ff,#0072ff,#00c6ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* SUBTITLE */
.header-sub {
    color: #ccc;
    font-size: 16px;
    margin-top: 5px;
}

/* CARD */
.card {
    background: linear-gradient(135deg,#1f4037,#2c5364);
    padding:20px;
    border-radius:15px;
    color:white;
    margin-bottom:15px;
    transition:0.4s;
}
.card:hover {
    transform: translateY(-8px);
    box-shadow:0 0 25px rgba(0,200,255,0.6);
}

/* SUGGESTION */
.suggest {
    padding:12px;
    border-radius:8px;
    margin-bottom:10px;
    background: rgba(255,77,79,0.1);
    border-left:5px solid #ff4d4f;
}

.good {
    background: rgba(82,196,26,0.1);
    border-left:5px solid #52c41a;
}

/* ANIMATION */
@keyframes fadeIn {
    from {opacity:0; transform:translateY(10px);}
    to {opacity:1;}
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="header-box">
    <div class="header-title">Medical Insurance Cost Predictor</div>
    <div class="header-sub">Smart Insights • Better Decisions</div>
</div>
""", unsafe_allow_html=True)

# ---------------- INPUT ----------------
st.subheader("📊 Enter Customer Details")

col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", 18, 65, 30)
    bmi = st.number_input("BMI", 10.0, 50.0, 25.0)

with col2:
    children = st.number_input("Children", 0, 5, 1)
    smoker = st.selectbox("Smoker", ["Yes", "No"])

with col3:
    sex = st.selectbox("Gender", ["Male", "Female"])

# ---------------- PREDICT ----------------
if st.button("🚀 Generate Report"):

    with st.spinner("Analyzing..."):
        time.sleep(1)

    smoker_val = 1 if smoker == "Yes" else 0
    sex_val = 1 if sex == "Male" else 0

    X = pd.DataFrame({
        "age":[age],
        "bmi":[bmi],
        "children":[children],
        "smoker":[smoker_val],
        "sex":[sex_val]
    })

    prediction = model.predict(X)[0]

    # ---------------- RISK ----------------
    if smoker == "Yes" or bmi > 30:
        risk = "HIGH RISK"
        risk_color = colors.red
    elif bmi > 25:
        risk = "MEDIUM RISK"
        risk_color = colors.orange
    else:
        risk = "LOW RISK"
        risk_color = colors.green

    # ---------------- FACTORS ----------------
    factors = []
    if smoker == "Yes":
        factors.append("🚬 Smoking increases cost significantly")
    if bmi > 25:
        factors.append("⚖️ Higher BMI increases health risk")
    if age > 50:
        factors.append("🧓 Age contributes to higher cost")
    if not factors:
        factors.append("✅ No major risk factors")

    # ---------------- SUGGESTIONS ----------------
    suggestions = []
    if smoker == "Yes":
        suggestions.append("🚭 Quit smoking to reduce premium")
    if bmi > 25:
        suggestions.append("🥗 Maintain healthy BMI")
    if age > 50:
        suggestions.append("🧑‍⚕️ Regular health checkups")
    if not suggestions:
        suggestions.append("✅ No changes required — healthy profile")

    # ---------------- UI OUTPUT ----------------
    st.success(f"💰 Estimated Cost: ₹{prediction:,.0f}")
    st.info(f"⚠️ Risk Level: {risk}")

    # Suggestions UI
    st.markdown("### 🧠 Recommendations")

    for s in suggestions:
        if "No changes" in s:
            st.markdown(f'<div class="suggest good">{s}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="suggest">{s}</div>', unsafe_allow_html=True)

    # ---------------- PDF ----------------
st.markdown("### 📄 Download Premium Report")

tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
doc = SimpleDocTemplate(tmp_pdf.name, pagesize=letter)
styles = getSampleStyleSheet()

content = []

# HEADER
header = Table([["Medical Insurance Cost Predictor"]])
header.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), colors.darkblue),
    ("TEXTCOLOR", (0,0), (-1,-1), colors.white),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("FONTSIZE", (0,0), (-1,-1), 16),
    ("BOTTOMPADDING", (0,0), (-1,-1), 10),
]))
content.append(header)
content.append(Spacer(1,15))

# ---------------- CUSTOMER PROFILE ----------------
content.append(Paragraph("Customer Profile", styles['Heading2']))
content.append(Spacer(1,10))

profile_data = [
    ["Feature", "Value"],
    ["Age", age],
    ["BMI", bmi],
    ["Children", children],
    ["Smoker", smoker],
    ["Gender", sex],
]

profile_table = Table(profile_data, colWidths=[200, 200])

profile_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.grey),
    ("TEXTCOLOR",(0,0),(-1,0),colors.white),
    ("GRID", (0,0), (-1,-1), 1, colors.black),
]))

content.append(profile_table)
content.append(Spacer(1,20))

# ---------------- COST + RISK ----------------
content.append(Paragraph("Summary", styles['Heading2']))
content.append(Spacer(1,10))

summary_data = [
    ["Estimated Cost", f"₹{prediction:,.0f}"],
    ["Risk Level", risk],
]

summary_table = Table(summary_data, colWidths=[200, 200])

summary_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), colors.lightgrey),
    ("GRID", (0,0), (-1,-1), 1, colors.black),
]))

content.append(summary_table)
content.append(Spacer(1,20))

# ---------------- RECOMMENDATIONS ----------------
content.append(Paragraph("Recommendations", styles['Heading2']))
content.append(Spacer(1,10))

for s in suggestions:
    content.append(Paragraph(f"• {s}", styles['Normal']))

# BUILD
doc.build(content)

with open(tmp_pdf.name, "rb") as f:
    st.download_button("📥 Download Report", f, "insurance_report.pdf")
