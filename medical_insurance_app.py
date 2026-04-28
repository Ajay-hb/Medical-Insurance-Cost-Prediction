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

# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align:center;
background: linear-gradient(90deg,#00c6ff,#0072ff);
-webkit-background-clip:text;
-webkit-text-fill-color:transparent;'>
🏥 Medical Insurance Cost Predictor
</h1>
<p style='text-align:center'>Smart Insights • Better Decisions</p>
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

    # ---------------- SHOW UI ----------------
    st.success(f"💰 Estimated Cost: ₹{prediction:,.0f}")
    st.info(f"⚠️ Risk Level: {risk}")

    # ---------------- PDF ----------------
    st.markdown("### 📄 Download Premium Report")

    tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    doc = SimpleDocTemplate(tmp_pdf.name, pagesize=letter)
    styles = getSampleStyleSheet()

    content = []

    # HEADER BAR
    header_table = Table([
        ["🏥 Medical Insurance Cost Predictor"]
    ])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.darkblue),
        ("TEXTCOLOR", (0,0), (-1,-1), colors.white),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTSIZE", (0,0), (-1,-1), 16),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ]))
    content.append(header_table)
    content.append(Spacer(1, 15))

    # SUMMARY BOX
    summary_table = Table([
        ["📊 Estimated Cost", f"₹{prediction:,.0f}"],
        ["⚠️ Risk Level", risk]
    ], colWidths=[200, 200])

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("TEXTCOLOR", (1,1), (1,1), risk_color),
    ]))

    content.append(summary_table)
    content.append(Spacer(1, 20))

    # PROFILE TABLE
    profile_data = [
        ["📋 Feature", "Value"],
        ["👤 Age", age],
        ["⚖️ BMI", bmi],
        ["👨‍👩‍👧 Children", children],
        ["🚬 Smoker", smoker],
        ["🧑 Gender", sex],
    ]

    profile_table = Table(profile_data, colWidths=[200, 200])
    profile_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ]))

    content.append(profile_table)
    content.append(Spacer(1, 20))

    # KEY DRIVERS
    driver_data = [["🔍 Key Drivers"]]
    for f in factors:
        driver_data.append([f])

    driver_table = Table(driver_data, colWidths=[400])
    driver_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ]))

    content.append(driver_table)
    content.append(Spacer(1, 20))

    # SUGGESTIONS
    suggest_data = [["🧠 Recommendations"]]
    for s in suggestions:
        suggest_data.append([s])

    suggest_table = Table(suggest_data, colWidths=[400])
    suggest_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ]))

    content.append(suggest_table)

    doc.build(content)

    with open(tmp_pdf.name, "rb") as f:
        st.download_button("📥 Download Premium Report", f, "insurance_report.pdf")
