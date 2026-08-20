## Day 1 — [date] — Environment Setup & Data Loading

### What I learned
- Why PowerShell and the Python interpreter can't understand each other's syntax, and how to tell which one I'm currently inside:because python syntax are not working in powershell
- The real root cause chain behind "No space left on device," from OSError to actual fix:real root cause that i dont have much space in C drive 
- Why Git doesn't track empty folders, and what that explained about app/, models/, notebooks/, src/ disappearing from GitHub while data/ survived:beacuse empty folder its just a path thats y this all folder didnt commit to git
- What each line in .gitignore is actually protecting against — specifically why mlruns/ and the raw CSV, not just "because Claude said so": Because this is too large file thats y gitingore tell github not to comiit this 
- Why the dataset's real shape (404,800 rows, 27 columns) didn't match the brief's stated 400,000 rows / 22 features — and why that gap is worth noting before Day 2 cleaning, not brushing past:ynthetic capstone datasets often ship slightly different from their own spec sheet
- What the DtypeWarning on the age column is likely signaling, and why it's a real finding, not noise:Column 0 is age. A column that's supposed to be a clean number (age) having "mixed types" usually means some rows have something non-numeric hiding in there — a stray string, a blank, a typo like "twenty-five" instead of 25. This is a genuine finding, not noise

### Still fuzzy
- (specific piece only, if anything — leave blank if genuinely nothing)-All topic qucik summary i want to read

### Note
- Today was almost entirely environment/tooling friction (shell mismatches, disk space, Git's file model) — expected for a local-dev tabular project, unlike DeepFER's Colab setup. No real ML reasoning happened yet. That starts Day 2 with the dtype issue.



## Day 2 — [14-08-26] — Data Quality Assessment

### Must-remember check (I ask, you answer)

Q1: Why did age still show as `object` dtype even after using low_memory=False — what did that rule out?
A1: Because they have different types, that's why it's showing object — because of the .0.0 bug. Also, pandas normally reads huge CSVs in chunks and can guess the wrong dtype from an early chunk — that would just be a pandas reading quirk, not a real problem. But even after forcing a full scan with low_memory=False, age was still object. That proves it's not pandas being confused — it's a genuine bug sitting in the actual data values.

Q2: What does errors='coerce' do inside pd.to_numeric, in your own words?
A2: Wherever it can't convert a value cleanly to a number, it just puts NaN (empty) there instead of crashing, and keeps going through the rest of the column.

Q3: What was actually wrong with the 3 bad age values, and why does that specific pattern matter for how we'll fix it on Day 3?
A3: Values like "58.0.0" aren't a valid number at all — no real number has two decimal points. This matters because it's a consistent pattern (likely a data generation bug), not random junk — so we can fix it predictably by stripping the extra ".0" instead of guessing case-by-case.

Q4: Why is 77% accuracy potentially meaningless on this dataset's emi_eligibility column?
A4: Because 77% of the data is already Not_Eligible — a model that just predicts "Not_Eligible" for every single applicant, without learning anything real, would still score ~77% accuracy. High accuracy alone doesn't prove the model actually learned to tell the classes apart, especially the rare 4.3% High_Risk group.

### Fuzziest part of today
Q: What genuinely confused you or took a re-explanation today?
A: Coerce definition and object explanation

### Findings to carry into Day 3
- Missing values (5 columns): monthly_rent (2426), bank_balance (2426), credit_score (2420), education (2404), emergency_fund (2351)
- Suspicious pattern flagged: monthly_rent and bank_balance have the exact same missing count — under investigation right now to confirm if it's the same rows or coincidence
- Duplicates: 0 found
- Target imbalance (emi_eligibility): Not_Eligible 77.3%, Eligible 18.4%, High_Risk 4.3%
- max_monthly_emi: right-skewed, hard floor at ₹500 (25th percentile also sits at 500), max (91,040) is ~12x the mean (6763) — confirmed visually via histogram

### One-line takeaway
-if CSV is too big then pandas do by chunks and chunks and we forced low_memory=False, which does a full-column scan instead of pandas' default chunked reading

## Day 3 — [15-08-26] — Cleaning Strategy & Imputation

### Must-remember check (I ask, you answer)
Q1: Why did we predict "same rows" for monthly_rent/bank_balance, and what did the actual overlap check reveal?
A1:because missing value is same so we thought its same rows but onky 15 rows are same all others are diff

Q2: Walk through the age fix regex in your own words — what pattern was it looking for, and what did it do?
A2:we find out in age column there values are string plus decimal so we reomve extra decimal from the end. Then pd.to_numeric converted the now-valid text into real numbers.

Q3: Why median instead of mean for monthly_rent, bank_balance, credit_score, emergency_fund?
A3:you already saw max_monthly_emi is right-skewed with outliers dragging the mean upward; these financial columns (rent, balance, credit score) are very likely skewed the same way, and median resists outliers better than mean does.

Q4: Why "Unknown" instead of filling education with the most common value?
A4:Silently assigning a guessed education level to real people is a worse assumption than just labeling it honestly as missing.

Q5: Why did the first imputation attempt crash with a TypeError, and what fixed it?
A5: .median() failed because it tried to compute a median on values like '303200.0' — with quotes, meaning that column is stored as text (object dtype), not real numbers. Same category of issue as age

### Fuzziest part of today
A:median concept and also age error solving

### Findings to carry into Day 4
- age bug: fixed, 0 remaining NaN
- monthly_rent/bank_balance overlap: only 15 shared rows — separate issues, not one systematic gap
- All missing values resolved (0 across dataset)
- Cleaned file saved: data/processed/emi_cleaned.csv, gitignored (same reasoning as raw)

### One-line takeaway
-numbers that look like numbers in a CSV can still be text underneath — always verify the dtype before running math on a column, don't assume.


## Day 4 — [17-08-26] — Feature Engineering

### Must-remember check (I ask, you answer)
Q1: Why does raw monthly_salary get flagged as object dtype even though it has zero missing values — what does that reveal about the relationship between "missing values" and "correct dtype"?
A1:no missing values" and "correct dtype" are two completely separate checks — passing one tells you nothing about the other.

Q2: In your own words, why is a ratio like loan_to_income_ratio a stronger signal for a model than the raw requested_amount column alone?
A2:is this loan request reasonable relative to what they earn," which is close to the actual business question (emi_eligibility) itself

Q3: Why is a large negative disposable_income not treated as a data error?
A3:Because it can happened if someone spening more than earning

Q4: What does the notebook losing bank_balance's fixed dtype (reverting to object) after the earlier hang/restart teach you about trusting an active notebook session versus a saved checkpoint file?
A4:this notebook session's df is in a partially-inconsistent state — likely a side effect of the earlier hang + Interrupt/Restart, where some cells got re-run and others didn't, so what's currently in memory doesn't fully match what Day 3 actually produced and saved to disk.

### Fuzziest part of today
A:All 5 formulas

### Findings to carry into Day 5
- 5 new engineered features created: debt_to_income_ratio, loan_to_income_ratio, disposable_income, savings_rate, dependents_ratio
- monthly_salary had a hidden object-dtype bug despite 0 missing values — fixed via pd.to_numeric + median fill
- savings_rate is heavily right-skewed (max 218x mean) — flagged for possible scaling before linear models
- Final feature-engineered dataset saved to data/processed/emi_features.csv

### One-line takeaway
-missing-value checks and dtype checks are two completely separate things, and passing one tells you nothing about the other.

## Day 5 — [18-08-26] — Baseline Classification Models

### Must-remember check (I ask, you answer)
Q1: Why do we drop emi_eligibility and max_monthly_emi from X before training — what would happen if we left them in?
A1:We remove the answer from the facts on purpose — if the model could see the answer while learning, it would just cheat by copying it,

Q2: What does stratify=y_class actually protect against, and how did we prove it worked?
A2:stratify forces the split to preserve that same 77/18/4.3 ratio in both the training and test sets

Q3: Explain, in your own words, why the plain Logistic Regression looked good (86% accuracy) but was actually a bad model.
A3:sounds great — but it caught zero actual High_Risk applicants. It just learned "when in doubt, guess the common answer,"

Q4: Why did Random Forest's accuracy (93%) hide a similar problem to the first model?
A4:High_Risk is only 4.3% of all applicants, most of those 100 judges barely ever see a High_Risk example while they're learning.

Q5: What made XGBoost genuinely different from the other three — not just a better number, but a better result?
A5:trees are built one after another, and each new tree specifically tries to fix the mistakes the previous ones made. It's stricter about one thing: it needs the answer column as plain numbers (0, 1, 2), not text words.

### Fuzziest part of today
A:All thre model explanation

### Findings to carry into Day 6
- 4 classification models trained and compared: plain LogReg, balanced LogReg, balanced Random Forest, balanced XGBoost
- Winner so far: XGBoost — 93% accuracy AND 0.94 High_Risk recall
- Key lesson: accuracy alone is misleading on imbalanced data — always check per-class recall
- All runs logged in MLflow (mlflow.db) for comparison

### One-line takeaway
-never trust accuracy alone on imbalanced data — always check recall on the rare class specifically


## Day 6 — [20-08-26] — Regression Modeling

### Must-remember check (I ask, you answer)
Q1: Why doesn't "accuracy" apply to regression the way it did for classification — what do we measure instead?
A1:

Q2: In your own words, what's the difference between what MAE measures and what RMSE measures?
A2:

Q3: Why did Linear Regression perform noticeably worse than the two tree-based models, given what we already knew about max_monthly_emi's distribution?
A3:

Q4: XGBoost had the better RMSE, but Random Forest had the better MAE — what does that difference actually tell us about how each model handles outliers vs. typical cases?
A4:

### Fuzziest part of today
A:

### Findings to carry into Day 7
- 3 regression models trained: Linear Regression, Random Forest, XGBoost
- Results — Linear: RMSE 4178, MAE 3000, R² 0.70 | Random Forest: RMSE 934, MAE 210, R² 0.985 | XGBoost: RMSE 710, MAE 248, R² 0.9915
- Winner: XGBoost (best RMSE, most consistent on outliers) — provisional pick for final regressor

### One-line takeaway
-


## Day 7 — [20-08-26] — Final Model Selection & Saving

### Must-remember check (I ask, you answer)
Q1: Why doesn't the deployed app depend on MLflow at runtime — what's the actual handoff point between training and serving?
A1:

Q2: In your own words, why does feature_columns.pkl need to exist — what real problem would happen without it?
A2:

Q3: In your own words, why does label_encoder.pkl need to exist — what real problem would happen without it?
A3:

Q4: Why did we have to retrain the classifier from scratch today instead of reusing the one from Day 5?
A4:

### Fuzziest part of today
A:

### Findings to carry into Day 8
- Final models saved: models/classifier_xgb.pkl, models/regressor_xgb.pkl
- Support files saved: models/label_encoder.pkl, models/feature_columns.pkl
- Classifier confirmed matching Day 5 performance: 93% accuracy, 0.93 High_Risk recall
- Both models are now fully self-contained — ready to be loaded directly by the Streamlit app, no MLflow dependency

### One-line takeaway
-