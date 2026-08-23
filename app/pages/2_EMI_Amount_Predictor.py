import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="EMI Predictor", page_icon="💵")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap');

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.01em; }

.eyebrow { text-transform: uppercase; letter-spacing: 0.14em; font-size: 12px; color: #C9A24B; font-weight: 600; margin-bottom: 6px; }
.hero-title { font-family: 'Space Grotesk', sans-serif; font-size: 40px; font-weight: 700; color: #EDF1F7; margin: 0 0 8px 0; }
.divider-thin { border: none; border-top: 1px solid #1E2A40; margin: 26px 0; }

.money-hero { margin: 4px 0 28px 0; }
.money-hero .lbl { color: #8592A6; font-size: 13px; text-transform: uppercase; letter-spacing: 0.1em; }
.money-hero .val { font-family: 'JetBrains Mono', monospace; font-size: 52px; font-weight: 700; color: #C9A24B; }

.compare-wrap { margin: 20px 0; }
.compare-row { display: flex; align-items: center; margin: 14px 0; gap: 14px; }
.compare-label { width: 190px; color: #8592A6; font-size: 13px; }
.compare-track { flex: 1; background: #1A2436; border-radius: 6px; height: 20px; overflow: hidden; }
.compare-fill { height: 100%; border-radius: 6px; }
.compare-fill.safe { background: #2FBF71; }
.compare-fill.req { background: #C9A24B; }
.compare-num { width: 110px; text-align: right; font-family: 'JetBrains Mono', monospace; font-weight: 600; color: #EDF1F7; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.markdown('<div class="eyebrow">Underwriting Console</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">💵 Maximum Safe EMI Predictor</div>', unsafe_allow_html=True)


@st.cache_resource
def load_artifacts():
    model = joblib.load("models/regressor_xgb.pkl")
    feature_cols = joblib.load("models/feature_columns.pkl")
    return model, feature_cols


model, feature_cols = load_artifacts()


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
    age = st.number_input("Age", 18, 70, 30, key="r_age")
    gender = st.selectbox("Gender", ["Male", "Female"], key="r_gender")
    marital_status = st.selectbox("Marital Status", ["Single", "Married"], key="r_marital")
with c2:
    education = st.selectbox("Education", ["Graduate", "Postgraduate", "High School", "Unknown"], key="r_edu")
    family_size = st.number_input("Family Size", 1, 15, 3, key="r_fam")
    dependents = st.number_input("Dependents", 0, 10, 1, key="r_dep")

st.subheader("Employment & Housing")
c3, c4 = st.columns(2)
with c3:
    employment_type = st.selectbox("Employment Type", ["Private", "Government", "Self-employed"], key="r_emp")
    company_type = st.selectbox("Company Type", ["MNC", "Mid-size", "Startup", "Large Indian", "Small"], key="r_comp")
    years_of_employment = st.number_input("Years of Employment", 0, 40, 5, key="r_yoe")
with c4:
    house_type = st.selectbox("House Type", ["Own", "Rented", "Family"], key="r_house")
    monthly_rent = st.number_input("Monthly Rent (₹)", 0, 200000, 10000, key="r_rent")

st.subheader("Financial Details")
c5, c6 = st.columns(2)
with c5:
    monthly_salary = st.number_input("Monthly Salary (₹)", 1000, 1000000, 50000, key="r_sal")
    credit_score = st.number_input("Credit Score", 300, 900, 700, key="r_cs")
    bank_balance = st.number_input("Bank Balance (₹)", 0, 10000000, 100000, key="r_bb")
    emergency_fund = st.number_input("Emergency Fund (₹)", 0, 5000000, 50000, key="r_ef")
with c6:
    school_fees = st.number_input("School Fees (₹/mo)", 0, 100000, 0, key="r_sf")
    college_fees = st.number_input("College Fees (₹/mo)", 0, 100000, 0, key="r_cf")
    travel_expenses = st.number_input("Travel Expenses (₹/mo)", 0, 100000, 3000, key="r_te")
    groceries_utilities = st.number_input("Groceries & Utilities (₹/mo)", 0, 100000, 8000, key="r_gu")
    other_monthly_expenses = st.number_input("Other Expenses (₹/mo)", 0, 100000, 2000, key="r_oe")
    existing_loans = st.selectbox("Existing Loans", ["Yes", "No"], key="r_el")
    current_emi_amount = st.number_input("Current EMI Amount (₹)", 0, 200000, 0, key="r_cea")

st.subheader("Loan Request")
c7, c8 = st.columns(2)
with c7:
    requested_amount = st.number_input("Requested Loan Amount (₹)", 1000, 5000000, 500000, key="r_ra")
    requested_tenure = st.number_input("Requested Tenure (months)", 3, 360, 36, key="r_rt")
with c8:
    emi_scenario = st.selectbox(
        "Loan Purpose",
        ["Personal Loan EMI", "Vehicle EMI", "Home Appliances EMI", "Education EMI", "E-commerce Shopping EMI"],
        key="r_es",
    )

if st.button("Predict Maximum Safe EMI", type="primary"):
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
    predicted_emi = model.predict(X_input)[0]
    predicted_emi = max(500, predicted_emi)

    st.markdown('<hr class="divider-thin">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="money-hero">
        <div class="lbl">Maximum Safe Monthly EMI</div>
        <div class="val">₹{predicted_emi:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

    approx_monthly_for_requested = requested_amount / requested_tenure
    max_val = max(predicted_emi, approx_monthly_for_requested) * 1.15
    pred_pct = predicted_emi / max_val * 100
    req_pct = approx_monthly_for_requested / max_val * 100

    st.subheader("How This Compares to Your Request")
    st.markdown(f"""
    <div class="compare-wrap">
        <div class="compare-row">
            <div class="compare-label">Predicted Safe EMI</div>
            <div class="compare-track"><div class="compare-fill safe" style="width:{pred_pct}%;"></div></div>
            <div class="compare-num">₹{predicted_emi:,.0f}</div>
        </div>
        <div class="compare-row">
            <div class="compare-label">Requested ÷ Tenure</div>
            <div class="compare-track"><div class="compare-fill req" style="width:{req_pct}%;"></div></div>
            <div class="compare-num">₹{approx_monthly_for_requested:,.0f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if approx_monthly_for_requested > predicted_emi:
        st.warning("⚠️ Your requested loan's implied monthly payment exceeds your predicted safe EMI. "
                   "Consider a longer tenure or smaller amount.")
    else:
        st.success("✅ Your requested loan's implied monthly payment is within your predicted safe EMI range.")