# 🚗 Title Pilot

**AI-ready title packet auditing for independent auto dealers.**

Title Pilot is a software prototype for reviewing vehicle title/deal packets before submission. The first version focuses on the repetitive document-review problem: extracting key fields, detecting obvious missing information, and producing a prioritized review checklist.

> **Important:** Title Pilot V0.1 is a prototype, not a DMV filing service, title agency, legal service, or guarantee of title acceptance. State requirements vary and must be verified against official requirements before production use.

---

## Why Title Pilot?

Independent dealers regularly deal with title packets containing multiple documents, signatures, lien information, vehicle identifiers, and state-specific requirements.

The product idea behind Title Pilot is to move the first layer of review from a manual checklist toward software-assisted auditing.

### V0.1 workflow

```text
Upload packet
     ↓
Extract document text
     ↓
Classify documents
     ↓
Extract key vehicle/deal fields
     ↓
Run completeness checks
     ↓
Prioritized audit report
```

The current MVP deliberately does **not** file anything with a DMV.

---

## What V0.1 does

- Upload PDF, image, TXT, or Markdown files
- Extract text from PDFs
- OCR image documents when local Tesseract is installed
- Classify basic document types
- Detect:
  - VIN
  - model year
  - make
  - model
  - owner/buyer
  - lienholder
- Flag missing or uncertain information
- Identify documents with little/no extractable text
- Produce a downloadable audit report
- Run locally without an API key

### Example statuses

| Status | Meaning |
|---|---|
| 🟢 READY TO REVIEW | No obvious completeness problem detected |
| 🟡 NEEDS REVIEW | Potential issues require human verification |
| 🔴 BLOCKED — MANUAL REVIEW | A significant required element was not detected |

These statuses are **internal product statuses**, not claims about DMV acceptance.

---

## Tech stack

- **Python 3.10+**
- **Streamlit** — application UI
- **pypdf** — PDF text extraction
- **Pillow** — image handling
- **Tesseract OCR / pytesseract** — optional image OCR
- Regular expressions — V0.1 deterministic extraction/auditing

No database, cloud deployment, paid AI API, or DMV integration is required for V0.1.

---

## Project structure

```text
title-pilot/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
└── title_pilot/
    ├── __init__.py
    ├── parser.py
    └── auditor.py
```

---

## Run locally

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/title-pilot.git
cd title-pilot
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the app

```bash
streamlit run app.py
```

The browser should open the local Title Pilot interface.

---

## OCR setup

PDF text extraction works without Tesseract.

Image OCR requires Tesseract to be installed on the machine.

If Tesseract is unavailable, Title Pilot will still run, but image documents may contain little or no extracted text and will be flagged for manual review.

---

## Testing the MVP

Create two test packets.

### Test A — clean packet

Include text containing:

```text
Certificate of Title
VIN: 1HGCM82633A123456
Year: 2023
Make: Example
Model: Sedan
Owner: Example Dealer
```

Expected result: no high-severity missing-field issue.

### Test B — incomplete packet

Use:

```text
Certificate of Title
Year: 2023
Make: Example
Model: Sedan
```

Expected result:

- VIN not detected
- owner/buyer not detected
- packet should require manual review

Do not use real customer PII while testing.

---

## Product architecture

The V0.1 architecture is intentionally simple:

```text
                ┌──────────────────┐
                │ Dealer uploads   │
                │ title packet     │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ Document parser  │
                │ PDF / TXT / OCR  │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ Document         │
                │ classifier       │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ Deal record      │
                │ extraction       │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ Audit engine     │
                │ missing/conflict │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ Review dashboard │
                │ + report         │
                └──────────────────┘
```

---

# Roadmap

## V0.1 — Packet Auditor

Current scope:

- [x] Upload documents
- [x] PDF extraction
- [x] Basic image OCR
- [x] Document classification
- [x] Key-field extraction
- [x] Basic audit rules
- [x] Downloadable report

## V0.2 — Consistency Engine

Next:

- [ ] Compare VIN across every document
- [ ] Compare owner names
- [ ] Compare lienholder names
- [ ] Compare year/make/model
- [ ] Detect conflicting dates
- [ ] Detect duplicate documents
- [ ] Confidence scores
- [ ] Evidence snippets showing where each field was found

Example:

```text
VIN
✓ Title:        1HGCM82633A123456
✓ Bill of Sale: 1HGCM82633A123456
✗ Lien Release: 1HGCM82633A123999

CONFLICT DETECTED
```

## V0.3 — State Rules Engine

Instead of hard-coding every state into the core application:

```text
State
 ↓
Rule set
 ↓
Required documents
 ↓
Required fields
 ↓
Known filing constraints
 ↓
Audit result
```

Each state rule set should be versioned and sourced from authoritative state documentation.

**Do not treat the rules engine as authoritative until every rule has been verified and reviewed.**

## V0.4 — AI Review Layer

Add an AI model only where it provides value:

- document understanding
- handwriting/field interpretation
- ambiguous field extraction
- explanation of why an issue was flagged
- structured JSON output
- confidence estimation

The deterministic audit engine should remain the final control layer for known rules.

## V1 — Dealer Workflow

Potential features:

- dealer accounts
- deal dashboard
- packet status
- task assignment
- audit history
- reviewer approval
- comments
- document versioning
- secure storage
- export
- notifications

## V2 — Production infrastructure

Potential architecture:

```text
React / Next.js
       ↓
API
       ↓
Authentication
       ↓
Document service
       ↓
OCR + AI extraction
       ↓
Rules engine
       ↓
PostgreSQL
       ↓
Audit/event log
```

Production implementation should add encryption, access control, retention policies, secure document storage, monitoring, backups, and formal privacy/security review.

---

# Core product principle

### AI should assist the reviewer, not silently become the authority.

For title workflows, a false negative can be operationally expensive.

Therefore:

```text
AI extraction
      +
deterministic validation
      +
human review
```

is preferable to:

```text
AI says OK → submit automatically
```

especially in the early versions.

---

# Security and privacy

Title packets can contain sensitive personal and vehicle information.

For this reason:

- Do not commit real title packets to GitHub.
- Do not put customer names, addresses, driver's-license information, or financial information into test fixtures.
- Keep uploaded documents outside Git.
- Use `.gitignore` for local upload/data directories.
- Production storage should use encryption at rest and in transit.
- Production access should use least-privilege permissions.
- Maintain an audit trail for document access and changes.
- Define document retention/deletion policies before handling real customer data.

---

# Current limitations

V0.1 is intentionally not a production title-processing system.

It does **not**:

- communicate with a DMV
- submit title applications
- access EFS/ELT systems
- guarantee acceptance
- verify legal ownership
- determine legal validity of a lien release
- provide legal advice
- know every state-specific title requirement
- replace a qualified title professional
- guarantee OCR accuracy

A detected field means only that the software found a likely matching piece of text.

---

# Research direction

The underlying product hypothesis is that title administration contains a repetitive document-review layer that can be software-assisted.

The original IdeaBrowser research also identifies:

- independent used-car dealers as the target customer group
- title/document review as a recurring operational pain
- state-by-state complexity as a major barrier
- established title-service competitors
- licensing, bonding, filing access, and liability as significant barriers to a fully managed title desk

This repository intentionally starts on the **software/document-auditing side** of that problem rather than attempting to become a title filing agency.

---

# Development principles

1. **Build narrow before broad.**
2. **Never invent state requirements.**
3. **Keep evidence attached to every extracted field.**
4. **Prefer deterministic validation for known rules.**
5. **Make uncertain results visible.**
6. **Never silently alter source documents.**
7. **Protect customer data by default.**
8. **Measure false positives and false negatives.**
9. **Version state-specific rules.**
10. **Keep a human in the loop until reliability is demonstrated.**

---

# Suggested GitHub milestones

### Milestone 1 — Working prototype
- Upload
- Extract
- Audit
- Report

### Milestone 2 — Reliable extraction
- VIN
- owner
- lienholder
- vehicle attributes
- evidence locations
- confidence scores

### Milestone 3 — Cross-document validation
- VIN consistency
- owner consistency
- lien consistency
- duplicate detection

### Milestone 4 — State rules
- one state
- versioned rules
- official-source references
- automated tests

### Milestone 5 — Dealer workflow
- dashboard
- packet status
- review queue
- audit history

---

# License

Choose a license before publishing the repository.

For a portfolio/research prototype, an open-source license such as MIT may be appropriate. For a commercial product, review the licensing strategy before selecting one.

---

## Disclaimer

Title Pilot is an independent software prototype. It is not affiliated with or endorsed by any DMV, state motor-vehicle agency, title company, dealership software vendor, or other organization mentioned in research.

State requirements change. Always verify applicable requirements with the relevant official authority before relying on software output for a real transaction.
