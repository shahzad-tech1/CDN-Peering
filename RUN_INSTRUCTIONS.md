# CDN Peering Management Console (EdgePeer IX-Fabric)
## Project Setup, Execution & Testing Instructions

> **Course:** SE3002 — Software Quality Engineering  
> **Assignment:** Assignment #01: Quality Evaluation of AI-Generated Software  
> **Evaluators / Authors:** Shahzad Ahmad (24I-3090) & Maham Munir (21I-1213) | **Section:** SE-5B  
> **System Under Test:** CDN Peering Management Console (Internetworking of CDNs through Peering)  
> **Tech Stack:** Python 3.10+, Flask 3.1.3, PostgreSQL 14/15/16, SQLAlchemy 2.0 ORM, Jinja2, Bootstrap 5  

---

## 1. System Overview & Architecture

The **EdgePeer IX-Fabric** console is an internetworking platform designed to facilitate dynamic peering, resource registry, policy enforcement, and bilateral settlement between autonomous Content Delivery Networks (CDNs).

### Key Functional Components:
* **Service Registry (R1 / R2):** Registration and discovery of CDN compute nodes, cache storage capacities, and upload/download transfer rates.
* **Policy Repository (R3):** Ingress traffic ceilings, minimum available CPU thresholds, and maximum capacity delegation limits per CDN provider.
* **Mediator & Peering Negotiation (R4 / R5):** Automated bilateral peering evaluations, SLA matching, and counter-proposal generation.
* **Accounting System (R6):** Cumulative Transfer Unit (TU) tracking across active peering arrangements.
* **Contract Dissolution & Re-negotiation (R7):** Automatic arrangement status evaluation and contract dissolution upon capacity/quota exhaustion.

---

## 2. Prerequisites

Ensure your development machine has the following installed:
1. **Python 3.10, 3.11, 3.12, or 3.14**:
   Verify installation:
   ```bash
   python --version
   ```
2. **PostgreSQL Server (v14, v15, or v16)**:
   Ensure the PostgreSQL service is active and running locally on port `5432`.
   Verify installation / client:
   ```bash
   psql --version
   ```
3. **Git** (optional, for version control):
   ```bash
   git --version
   ```

---

## 3. Step-by-Step Installation & Run Guide

### Step 1: Clone or Open Project Directory
Navigate to the root directory where the project resides:
```powershell
cd "d:\Semester 5\SQE\Assignments\Assignment 1\cdn-peering"
```

---

### Step 2: Set Up Python Virtual Environment

It is strongly recommended to isolate dependencies inside a virtual environment:

#### Windows (PowerShell):
```powershell
# Create virtual environment named 'venv'
python -m venv venv

# If script execution is restricted in PowerShell, enable it for this session:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

#### Windows (Command Prompt - CMD):
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### Linux / macOS (Bash / Zsh):
```bash
python3 -m venv venv
source venv/bin/activate
```

*(Once activated, you will see `(venv)` prefixed in your terminal prompt).*

---

### Step 3: Install Required Dependencies

Install the locked packages from [requirements.txt](file:///d:/Semester%205/SQE/Assignments/Assignment%201/cdn-peering/requirements.txt):
```bash
pip install -r requirements.txt
```

---

### Step 4: Configure PostgreSQL Database & Environment

1. **Start your local PostgreSQL service** (if not already running):
   * On Windows: Open `services.msc` and verify `postgresql-x64-XX` is **Running**, or run:
     ```powershell
     net start postgresql-x64-16
     ```
2. **Create the Database:**
   Connect to PostgreSQL using `psql` or `pgAdmin` and execute:
   ```sql
   CREATE DATABASE cdn_peering;
   ```
   *Via terminal:*
   ```bash
   psql -U postgres -c "CREATE DATABASE cdn_peering;"
   ```

3. **Configure Environment Variables (`.env`):**
   Copy the example template file:
   * **Windows:**
     ```powershell
     copy .env.example .env
     ```
   * **Linux/macOS:**
     ```bash
     cp .env.example .env
     ```
   Open `.env` and verify your PostgreSQL credentials:
   ```env
   DATABASE_URL=postgresql://<YOUR_POSTGRES_USER>:<YOUR_POSTGRES_PASSWORD>@localhost:5432/cdn_peering
   SECRET_KEY=your-secret-flask-key-here
   ```
   > **Note:** If your local PostgreSQL uses user `postgres` and password `postgres`, the default in `.env.example` will work out of the box.

---

### Step 5: Seed Demo Data & Initialize Database

Populate the database with demo CDN providers (Cloudflare Edge, Fastly POP, Akamai, AWS CloudFront, Lumen, etc.), policy rules, compute/storage resources, and sample peering arrangements:

```bash
python seed.py
```

**Expected Output:**
```text
Seeding complete:
  - 8 CDN Providers created
  - 11 Resources registered
  - 5 Policy Rules configured
  - 6 Peering Arrangements created
  - 6 Negotiation Logs recorded
```

---

### Step 6: Start the Flask Web Application

Run the application:
```bash
python app.py
```

**Expected Output:**
```text
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

Open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 4. Web Console Navigation & Features

Once the application is running, you can explore the full functional workflow:

| Feature / Page | URL Route | Description |
|---|---|---|
| **Dashboard** | `/` | Real-time IX-Fabric metrics, total compute/storage capacity, active peering arrangements, and provider summaries. |
| **CDN Providers** | `/providers` | View all registered autonomous CDN systems, ASNs, statuses, and register new providers. |
| **Resource Registry** | `/resources` | View registered CDN edge compute cores, cache storage, upload/download limits, and provision new capacity (R1). |
| **Peering Simulator** | `/peering` | Simulate real-time bilateral peering requests between origin and target CDNs. Tests policy rules (R3, R4, R5), CPU delegations, and ingress ceilings. |
| **Arrangements & Settlement** | `/arrangements` | Inspect active and disbanded peering contracts, log Transfer Units (TU) usage (R6), and trigger contract evaluations (R7). |

---

## 5. Running Automated Functional Tests & Probes

To verify the test suite derived in **Part 3-B** ([Functional_Test_Derivation_Execution_and_Traceability.txt](file:///d:/Semester%205/SQE/Assignments/Assignment%201/cdn-peering/Functional_Test_Derivation_Execution_and_Traceability.txt)), run the automated test probe:

```bash
python test_evidence_probe.py
```

### Key Test Case Verifications:
* **TC-01:** Valid edge resource registration (CPU, Storage, Bandwidth).
* **TC-02:** Negative CPU input boundary rejection.
* **TC-05:** Self-peering prevention (Origin ASN == Target ASN validation).
* **TC-06:** Policy boundary rejection (Akamai max delegated threshold exceeded).
* **TC-07:** Successful policy acceptance and arrangement creation.
* **TC-10:** Transfer Unit (TU) settlement accounting update.
* **TC-12:** Contract capacity threshold evaluation and status transition to `disbanded`.
* **TC-14:** Malicious ingress request rate ceiling violation rejection (`>15,000 req/s`).

---

## 6. Project Directory Structure

```text
cdn-peering/
│
├── app.py                      # Application factory (Flask app setup & blueprints)
├── config.py                   # Configuration loader (PostgreSQL URI, secret key)
├── models.py                   # SQLAlchemy ORM models (Providers, Resources, Policies, etc.)
├── seed.py                     # Database population script with initial mock data
├── test_evidence_probe.py      # Automated test execution probe for Part 3-B
├── check_tc14.py               # Boundary verification script
├── requirements.txt            # Python package dependencies
├── .env.example                # Template for environment variables
├── .env                        # Local environment variables (Not to be shared)
├── .gitignore                  # Git ignore specifications
├── RUN_INSTRUCTIONS.md         # Detailed execution guide (this file)
├── README.md                   # Repository overview & quickstart
│
├── routes/                     # Blueprint controllers
│   ├── dashboard.py            # Overview dashboard controller
│   ├── providers.py            # Provider management routes
│   ├── resources.py            # Service Registry resource routes
│   ├── peering.py              # Peering simulation & negotiation routes
│   └── arrangements.py         # Arrangement monitoring & accounting routes
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Master layout with navigation bar & theme
│   ├── dashboard/              # Dashboard metrics view
│   ├── providers/              # Provider catalog & registration views
│   ├── resources/              # Resource management & creation views
│   ├── peering/                # Peering simulator view
│   ├── arrangements/           # Arrangement list & detail views
│   └── errors/                 # Custom 404 and 500 error pages
│
└── static/                     # Static styling & scripts
    ├── css/                    # Custom styling sheets
    └── js/                     # Client-side scripts
```

---

## 7. Troubleshooting & Common Issues

### 1. `psycopg2.OperationalError: connection to server at "localhost", port 5432 failed`
* **Cause:** PostgreSQL service is stopped or not running on port 5432.
* **Fix:** Open Windows Services (`services.msc`), find **postgresql-x64-XX**, and click **Start**.

### 2. `psycopg2.OperationalError: FATAL: password authentication failed for user "postgres"`
* **Cause:** Incorrect database credentials in `.env`.
* **Fix:** Verify your PostgreSQL password and update the `DATABASE_URL` line inside `.env`.

### 3. `psycopg2.errors.DuplicateDatabase: database "cdn_peering" already exists`
* **Cause:** The database was already created in a previous run.
* **Fix:** This is normal and safe. You can proceed directly to `python seed.py` or re-seed existing tables.

### 4. `Address already in use` or Port 5000 Conflict
* **Cause:** Another process or previous Flask instance is occupying port 5000.
* **Fix:**
  * In PowerShell:
    ```powershell
    Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process
    ```
  * Or launch Flask on a different port:
    ```bash
    flask run --port 5001
    ```

### 5. PowerShell Script Execution Restriction
* **Error:** `File Activate.ps1 cannot be loaded because running scripts is disabled on this system.`
* **Fix:** Run this once in PowerShell:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```
