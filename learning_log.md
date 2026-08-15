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