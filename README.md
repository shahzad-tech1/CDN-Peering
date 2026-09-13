# EdgePeer IX-Fabric: CDN Peering Management Console

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-green.svg)](https://palletsprojects.com/p/flask/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/Course-SE3002%20SQE-orange.svg)]()

> **Course:** SE3002 — Software Quality Engineering  
> **Assignment:** Assignment #01: Quality Evaluation of AI-Generated Software  
> **Group Members:** Shahzad Ahmad (24I-3090) & Maham Munir (21I-1231) | **Section:** SE-5B  
> **Repository:** [https://github.com/shahzad-tech1/CDN-Peering](https://github.com/shahzad-tech1/CDN-Peering)

---

## Overview

**EdgePeer IX-Fabric** is a web-based Content Delivery Network (CDN) Peering Management Console that automates the discovery, negotiation, settlement, and capacity management of bilateral and multilateral CDN peering arrangements.

### Core Modules:
1. **Service Registry (SR - R1 & R2):** Real-time node capacity registry, storage tracking, and bandwidth auditing.
2. **Policy Repository (PR - R3):** Provider-level SLA constraints, CPU threshold delegation, and ingress rate protection.
3. **Mediator & Peering Agent (PA - R4 & R5):** Automated bilateral negotiation simulation, SLA parameter evaluation, and agreement creation.
4. **Accounting & Settlement (R6):** Transfer Unit (TU) ledger and capacity consumption accounting.
5. **Contract Dissolution & Re-negotiation (R7):** Automated capacity evaluation, quota enforcement, and contract dissolution.

---

## Quickstart Guide

For step-by-step installation, virtual environment configuration, and database setup, please refer to the detailed instructions in [RUN_INSTRUCTIONS.md](file:///d:/Semester%205/SQE/Assignments/Assignment%201/cdn-peering/RUN_INSTRUCTIONS.md).

### Quick Run Summary:

```bash
# 1. Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment (.env)
# Ensure DATABASE_URL in .env points to your running PostgreSQL instance
copy .env.example .env

# 4. Seed database with initial data
python seed.py

# 5. Launch the application
python app.py
```

Access the web interface at `http://127.0.0.1:5000/`.

---

## Automated Test Suite & Evidence

The functional test suite derived in **Part 3-B** can be executed against the active application:

```bash
python test_evidence_probe.py
```

See [Functional_Test_Derivation_Execution_and_Traceability.txt](file:///d:/Semester%205/SQE/Assignments/Assignment%201/cdn-peering/Functional_Test_Derivation_Execution_and_Traceability.txt) for the complete 29119-aligned test condition derivation, equivalence partitioning, boundary value analyses, and bi-directional traceability matrices.
