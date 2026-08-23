import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="Eligibility Predictor", page_icon="✅")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap');

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.01em; }

.eyebrow { text-transform: uppercase; letter-spacing: 0.14em; font-size: 12px; color: #C9A24B; font-weight: 600; margin-bottom: 6px; }
.hero-title { font-family: 'Space Grotesk', sans-serif; font-size: 40px; font-weight: 700; color: #EDF1F7; margin: 0 0 8px 0; }
.divider-thin { border: none; border-top: 1px solid #1E2A40; margin: 26px 0; }

.ledger-card { background: #121B2E; border-left: 3px solid #C9A24B; border-radius: 8px; padding: 18px 22px; margin: 8px 0; }
.ledger-label { color: #8592A6; font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
.ledger-value { font-family: 'JetBrains Mono', monospace; font-size: 22px; font-weight: 700; color: #EDF1F7; }

.result-eyebrow { text-transform: uppercase; letter-spacing: 0.14em; font-size: 12px; color: #8592A6; font-weight: 600; }
.result-title { font-family: 'Space Grotesk', sans-serif; font-size: 40px; font-weight: 700; margin: 4px 0 20px 0; }
.result-eligible { color: #2FBF71; }
.result-highrisk { color: #F5A623; }
.result-noteligible { color: #FF5C5C; }

.gauge-wrap { margin: 8px 0 32px 0; }
.gauge-track { height: 14px; border-radius: 7px; background: linear-gradient(90deg, #FF5C5C 0%, #F5A623 50%, #2FBF71 100%); position: relative; }
.gauge-marker { position: absolute; top: -7px; width: 4px; height: 28px; background: #EDF1F7; border-radius: 2px; box-shadow: 0 0 10px rgba(255,255,255,0.7); }
.gauge-labels { display: flex; justify-content: space-between; font-size: 11px; color: #8592A6; margin-top: 8px; text-transform: uppercase; letter-spacing: 0.08em; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.markdown('<div class="eyebrow">Underwriting Console</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">✅ Loan Eligibility Predictor</div>', unsafe_allow_html=True)


@st.cache_resource
def load_artifacts():
    model = joblib.load("models/classifier_xgb.pkl")
    le = joblib.load("models/label_encoder.pkl")
    feature_cols = joblib.load("models/feature_columns.pkl")
    return model, le, feature_cols


model, le, feature_cols = load_artifacts()


def build_input_row(raw):
    row = {col: 0 for col in feature_cols}

    numeric_fields = ['age', 'monthly_salary', 'years_of_employment', 'monthly_rent',
                       'family_size', 'dependents', 'school_fees', 'college_fees',
                       'travel_expenses', 'groceries_utilities', 'other_monthly_expenses',
                       'current_emi_amount', 'credit_score', 'bank_balance', 'emergency_fund',
                       'requested_amount', 'requested_tenure']
    for f in numeric_fields:
        if f in row:
            row[f] = raw.get(f, 0)

    row['debt_to_income_ratio'] = (raw['current_emi_amount'] + raw['monthly_rent']) / raw['monthly_salary']
    row['loan_to_income_ratio'] = raw['requested_amount'] / (raw['monthly_salary'] * 12)
    row['disposable_income'] = raw['monthly_salary'] - (
        raw['monthly_rent'] + raw['school_fees'] + raw['college_fees'] +
        raw['travel_expenses'] + raw['groceries_utilities'] +
        raw['other_monthly_expenses'] + raw['current_emi_amount']
    )
    row['savings_rate'] = raw['bank_balance'] / raw['monthly_salary']
    row['dependents_ratio'] = raw['dependents'] / raw['family_size']

    categorical_raw = {
        'gender': raw['gender'], 'marital_status': raw['marital_status'],
        'education': raw['education'], 'employment_type': raw['employment_type'],
        'company_type': raw['company_type'], 'house_type': raw['house_type'],
        'existing_loans': raw['existing_loans'], 'emi_scenario': raw['emi_scenario'],
    }
    for col_prefix, value in categorical_raw.items():
        matches = [c for c in feature_cols
                   if c.startswith(col_prefix + "_") and c.lower() == f"{col_prefix}_{value}".lower()]
        if matches:
            row[matches[0]] = 1

    return pd.DataFrame([row])[feature_cols]


st.subheader("Personal Details")
c1, c2 = st.columns(2)
with c1:
    age = st.number_input("Age", 18, 70, 30)
    gender = st.selectbox("Gender", ["Male", "Female"])
    marital_status = st.selectbox("Marital Status", ["Single", "Married"])
with c2:
    education = st.selectbox("Education", ["Graduate", "Postgraduate", "High School", "Unknown"])
    family_size = st.number_input("Family Size", 1, 15, 3)
    dependents = st.number_input("Dependents", 0, 10, 1)

st.subheader("Employment & Housing")
c3, c4 = st.columns(2)
with c3:
    employment_type = st.selectbox("Employment Type", ["Private", "Government", "Self-employed"])
    company_type = st.selectbox("Company Type", ["MNC", "Mid-size", "Startup", "Large Indian", "Small"])
    years_of_employment = st.number_input("Years of Employment", 0, 40, 5)
with c4:
    house_type = st.selectbox("House Type", ["Own", "Rented", "Family"])
    monthly_rent = st.number_input("Monthly Rent (₹)", 0, 200000, 10000)

st.subheader("Financial Details")
c5, c6 = st.columns(2)
with c5:
    monthly_salary = st.number_input("Monthly Salary (₹)", 1000, 1000000, 50000)
    credit_score = st.number_input("Credit Score", 300, 900, 700)
    bank_balance = st.number_input("Bank Balance (₹)", 0, 10000000, 100000)
    emergency_fund = st.number_input("Emergency Fund (₹)", 0, 5000000, 50000)
with c6:
    school_fees = st.number_input("School Fees (₹/mo)", 0, 100000, 0)
    college_fees = st.number_input("College Fees (₹/mo)", 0, 100000, 0)
    travel_expenses = st.number_input("Travel Expenses (₹/mo)", 0, 100000, 3000)
    groceries_utilities = st.number_input("Groceries & Utilities (₹/mo)", 0, 100000, 8000)
    other_monthly_expenses = st.number_input("Other Expenses (₹/mo)", 0, 100000, 2000)
    existing_loans = st.selectbox("Existing Loans", ["Yes", "No"])
    current_emi_amount = st.number_input("Current EMI Amount (₹)", 0, 200000, 0)

st.subheader("Loan Request")
c7, c8 = st.columns(2)
with c7:
    requested_amount = st.number_input("Requested Loan Amount (₹)", 1000, 5000000, 500000)
    requested_tenure = st.number_input("Requested Tenure (months)", 3, 360, 36)
with c8:
    emi_scenario = st.selectbox(
        "Loan Purpose",
        ["Personal Loan EMI", "Vehicle EMI", "Home Appliances EMI", "Education EMI", "E-commerce Shopping EMI"],
    )

if st.button("Predict Eligibility", type="primary"):
    raw = dict(age=age, gender=gender, marital_status=marital_status, education=education,
               monthly_salary=monthly_salary, employment_type=employment_type,
               years_of_employment=years_of_employment, company_type=company_type,
               house_type=house_type, monthly_rent=monthly_rent, family_size=family_size,
               dependents=dependents, school_fees=school_fees, college_fees=college_fees,
               travel_expenses=travel_expenses, groceries_utilities=groceries_utilities,
               other_monthly_expenses=other_monthly_expenses, existing_loans=existing_loans,
               current_emi_amount=current_emi_amount, credit_score=credit_score,
               bank_balance=bank_balance, emergency_fund=emergency_fund,
               emi_scenario=emi_scenario, requested_amount=requested_amount,
               requested_tenure=requested_tenure)

    X_input = build_input_row(raw)
    pred_encoded = model.predict(X_input)[0]
    pred_label = le.inverse_transform([pred_encoded])[0]
    proba = model.predict_proba(X_input)[0]
    proba_dict = dict(zip(le.classes_, proba))

    score = proba_dict.get('Eligible', 0) * 100 + proba_dict.get('High_Risk', 0) * 50
    score = max(0, min(100, score))

    label_class = {"Eligible": "result-eligible", "High_Risk": "result-highrisk",
                   "Not_Eligible": "result-noteligible"}[pred_label]
    icon = {"Eligible": "✅", "High_Risk": "⚠️", "Not_Eligible": "❌"}[pred_label]

    st.markdown('<hr class="divider-thin">', unsafe_allow_html=True)
    st.markdown('<div class="result-eyebrow">Assessment Result</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="result-title {label_class}">{icon} {pred_label.replace("_", " ")}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(f"""
    <div class="gauge-wrap">
        <div class="gauge-track"><div class="gauge-marker" style="left: calc({score}% - 2px);"></div></div>
        <div class="gauge-labels"><span>Not Eligible</span><span>High Risk</span><span>Eligible</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Prediction Confidence")
    for cls in ["Eligible", "High_Risk", "Not_Eligible"]:
        p = proba_dict.get(cls, 0) * 100
        st.write(f"{cls.replace('_', ' ')}: {p:.1f}%")
        st.progress(min(int(p), 100))

    st.subheader("Financial Snapshot")
    dti = round(X_input['debt_to_income_ratio'].values[0], 2)
    disp_inc = round(X_input['disposable_income'].values[0])
    savings = round(X_input['savings_rate'].values[0], 2)
    lti = round(X_input['loan_to_income_ratio'].values[0], 2)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="ledger-card"><div class="ledger-label">Debt-to-Income</div>'
                     f'<div class="ledger-value">{dti}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="ledger-card"><div class="ledger-label">Disposable Income</div>'
                     f'<div class="ledger-value">₹{disp_inc:,}</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="ledger-card"><div class="ledger-label">Savings Rate</div>'
                     f'<div class="ledger-value">{savings}</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="ledger-card"><div class="ledger-label">Loan-to-Income</div>'
                     f'<div class="ledger-value">{lti}</div></div>', unsafe_allow_html=True)

    if pred_label != "Eligible":
        st.info("💡 Improving your debt-to-income ratio or increasing disposable income can improve eligibility.")