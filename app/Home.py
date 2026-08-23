import streamlit as st

st.set_page_config(page_title="EMIPredict AI", page_icon="💠", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=swap');

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.01em; }

.eyebrow { text-transform: uppercase; letter-spacing: 0.14em; font-size: 12px; color: #C9A24B; font-weight: 600; margin-bottom: 6px; }
.hero-title { font-family: 'Space Grotesk', sans-serif; font-size: 44px; font-weight: 700; color: #EDF1F7; margin: 0 0 8px 0; line-height: 1.15; }
.hero-sub { color: #8592A6; font-size: 16px; max-width: 640px; line-height: 1.55; }
.divider-thin { border: none; border-top: 1px solid #1E2A40; margin: 26px 0; }

.ledger-card { background: #121B2E; border-left: 3px solid #C9A24B; border-radius: 8px; padding: 20px 24px; margin: 8px 0; }
.ledger-label { color: #8592A6; font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
.ledger-value { font-family: 'JetBrains Mono', monospace; font-size: 26px; font-weight: 700; color: #EDF1F7; }
.ledger-value.good { color: #2FBF71; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

st.markdown('<div class="eyebrow">AI Underwriting Console</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">EMIPredict AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">A dual-model system that reads an applicant\'s financial profile '
    'and returns two numbers a loan desk actually needs: eligibility risk, and the maximum '
    'EMI they can safely carry.</div>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="divider-thin">', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        '<div class="ledger-card"><div class="ledger-label">Classification Accuracy</div>'
        '<div class="ledger-value good">93.0%</div></div>',
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        '<div class="ledger-card"><div class="ledger-label">High-Risk Recall</div>'
        '<div class="ledger-value good">93.0%</div></div>',
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        '<div class="ledger-card"><div class="ledger-label">EMI Prediction R²</div>'
        '<div class="ledger-value good">0.99</div></div>',
        unsafe_allow_html=True,
    )

st.markdown('<hr class="divider-thin">', unsafe_allow_html=True)
st.markdown("### Use the sidebar")
st.markdown(
    "**Eligibility Predictor** — classify an applicant as Eligible, High Risk, or Not Eligible.  \n"
    "**EMI Amount Predictor** — estimate the maximum monthly EMI they can safely carry."
)