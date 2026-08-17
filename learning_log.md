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
A1:

Q2: In your own words, why is a ratio like loan_to_income_ratio a stronger signal for a model than the raw requested_amount column alone?
A2:

Q3: Why is a large negative disposable_income not treated as a data error?
A3:

Q4: What does the notebook losing bank_balance's fixed dtype (reverting to object) after the earlier hang/restart teach you about trusting an active notebook session versus a saved checkpoint file?
A4:

### Fuzziest part of today
A:

### Findings to carry into Day 5
- 5 new engineered features created: debt_to_income_ratio, loan_to_income_ratio, disposable_income, savings_rate, dependents_ratio
- monthly_salary had a hidden object-dtype bug despite 0 missing values — fixed via pd.to_numeric + median fill
- savings_rate is heavily right-skewed (max 218x mean) — flagged for possible scaling before linear models
- Final feature-engineered dataset saved to data/processed/emi_features.csv

### One-line takeaway
-