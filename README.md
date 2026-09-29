# Parking Chatbot - Stage 2: Human-in-the-Loop Admin Agent

![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-0.1.20-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-teal.svg)
[![CI Pipeline](https://github.com/EminnKurtt/parking-admin-agent-STAGE2/actions/workflows/ci.yml/badge.svg)](https://github.com/EminnKurtt/parking-admin-agent-STAGE2/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Overview

Welcome to **Stage 2** of the **Parking Space Reservation Chatbot - Multi-Agent AI System**.

In Stage 1, a Retrieval-Augmented Generation (RAG) Chatbot handled customer queries regarding parking regulations, availability, and general policy. 

**Stage 2** introduces the **Human-in-the-Loop (HITL) Admin Agent (Agent 2)**. While AI agents can autonomously gather reservation details from users, reserving a parking space often requires authorized human oversight or physical facility approval. Rather than granting the agent autonomous booking permissions, Stage 2 implements an escalation and polling pattern:

1. **LLM Message Formatting**: Formats raw customer reservation details into a concise, professional message for a human facility administrator.
2. **REST API Escalation**: Sends the structured request to a **Mock Admin Dashboard API** with authentication headers.
3. **Polling & Decision Feedback**: Periodically polls the Admin Dashboard to check whether the human administrator approved or rejected the request, subsequently returning the decision to the customer workflow.

---

## Architecture Diagram

```
+------------------+         +----------------------+         +-----------------------+
|     Agent 1      |         |       Agent 2        |         |   Mock Admin          |
| (RAG Chatbot /   |         |    (Admin Agent)     |         |   Dashboard API       |
|  User Intake)    |         |                      |         |   (FastAPI)           |
+--------+---------+         +----------+-----------+         +-----------+-----------+
         |                              |                                 |
         |  1. Escalate reservation     |                                 |
         |     details (Name, Car, Time)|                                 |
         +----------------------------->|                                 |
                                        |  2. LLM Formats Message         |
                                        |     (LangChain + OpenAI)        |
                                        |                                 |
                                        |  3. POST /admin/requests        |
                                        +-------------------------------->|
                                        |     (Request ID returned)       |
                                        |<--------------------------------+
                                        |                                 |
                                        |  4. Poll GET /admin/status/{id} |
                                        +-------------------------------->|
                                        |     Status: PENDING             |
                                        |<--------------------------------+
                                        |                                 |
                                        |         [Human Admin Reviews]   |
                                        |         [POST /admin/approve]   |
                                        |                                 |
                                        |  5. Poll GET /admin/status/{id} |
                                        +-------------------------------->|
                                        |     Status: APPROVED / REJECTED |
                                        |<--------------------------------+
         |                              |                                 |
         |  6. Decision reported back   |                                 |
         |<-----------------------------+                                 |
```

---

## Project Structure

```
parking-admin-agent/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── schemas.py
│
├── core/
│   ├── __init__.py
│   ├── admin_agent.py
│   └── config.py
│
├── tests/
│   ├── __init__.py
│   ├── test_admin_agent.py
│   └── test_mock_admin_api.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

---

## Prerequisites

- **Python**: Version `3.11` (or `>= 3.11`)
- **OpenAI API Key**: Required for live LangChain LLM message formatting (`gpt-3.5-turbo`)

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/EminnKurtt/parking-admin-agent-STAGE2.git
   cd parking-admin-agent
   ```

2. **Create and activate a virtual environment:**
   - **Linux / macOS:**
     ```bash
     python3.11 -m venv venv
     source venv/bin/activate
     ```
   - **Windows:**
     ```powershell
     py -3.11 -m venv venv
     .\venv\Scripts\activate
     ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to include your OpenAI API key and configure parameters:
   ```env
   OPENAI_API_KEY=sk-...
   ADMIN_API_URL=http://localhost:8001
   ADMIN_API_KEY=secret-admin-key
   ```

---

## Usage Workflow

Experience the Human-in-the-Loop interaction using two separate terminal windows:

### Terminal 1: Start Mock Admin Dashboard API
```bash
python run.py
```
The dashboard starts on `http://localhost:8001`. You can access interactive Swagger documentation at `http://localhost:8001/docs`.

### Terminal 2: Escalate a Reservation Request
Open a Python interactive shell or run an escalation script:
```python
from core.admin_agent import AdminAgent

agent = AdminAgent()

# Step 1: Escalate reservation request
req_id = agent.escalate_reservation(
    user_name="Sarah Connor",
    car_number="CA-55-CYBER",
    period="Tomorrow 09:00 - 17:00"
)

# Step 2: Poll for administrator decision
if req_id:
    approved = agent.wait_for_approval(req_id, max_retries=12, delay=5)
    if approved:
        print(f"Success! Reservation {req_id} confirmed.")
    else:
        print(f"Notice: Reservation {req_id} was rejected or timed out.")
```

### Terminal 3 (or Browser / curl): Human Admin Decision
While Terminal 2 is polling, approve or reject the request:
```bash
curl -X POST "http://localhost:8001/admin/approve/{request_id}?action=APPROVED" \
     -H "X-API-Key: secret-admin-key"
```
Or open `http://localhost:8001/docs` in your browser:
1. Locate `POST /admin/approve/{request_id}`.
2. Enter the `request_id`, set `action` to `APPROVED` or `REJECTED`, and click **Execute**.
3. Watch Terminal 2 instantly detect the approval decision!

---

## API Reference

The Mock Admin Dashboard exposes the following REST API endpoints:

| Method | Endpoint | Description | Headers |
|---|---|---|---|
| `GET` | `/` | Health check and directory of endpoints | None |
| `POST` | `/admin/requests` | Submit a new reservation request | `X-API-Key: secret-admin-key` |
| `GET` | `/admin/status/{request_id}` | Check status (`PENDING`, `APPROVED`, `REJECTED`) | `X-API-Key: secret-admin-key` |
| `POST` | `/admin/approve/{request_id}` | Approve or reject request (`action=APPROVED\|REJECTED`) | `X-API-Key: secret-admin-key` |
| `GET` | `/admin/requests` | List all tracked requests (Debug/Admin) | `X-API-Key: secret-admin-key` |

---

## Testing

The project contains unit tests verifying the Mock Admin Dashboard API and the LangChain Admin Agent with mocked HTTP and LLM calls.

To run the test suite:
```bash
pytest tests/ -v
```

### Expected Output:
```text
============================= test session starts =============================
platform win32 -- Python 3.11.9, pytest-8.2.0, pluggy-1.6.0 -- ...
rootdir: C:\Users\...\parking-admin-agent
collected 6 items

tests/test_admin_agent.py::test_format_request_message PASSED            [ 16%]
tests/test_admin_agent.py::test_escalate_reservation_success PASSED      [ 33%]
tests/test_admin_agent.py::test_escalate_reservation_api_failure PASSED  [ 50%]
tests/test_admin_agent.py::test_get_approval_status PASSED               [ 66%]
tests/test_mock_admin_api.py::test_unauthorized_access PASSED            [ 83%]
tests/test_mock_admin_api.py::test_create_and_approve_flow PASSED        [100%]

============================== 6 passed in 0.85s ==============================
```

---

## CI/CD Pipeline

The project includes continuous integration configured via GitHub Actions in [ci.yml](file:///.github/workflows/ci.yml):
- Runs automatically on `push` and `pull_request` targeting the `main` branch.
- Sets up Python `3.11`.
- Installs dependencies from `requirements.txt`.
- Injects repository secrets and runs the full test suite via `pytest tests/ -v`.

---

## Integration with Stage 1

In the larger multi-agent system, the Stage 1 RAG Chatbot hands off confirmed intent to the Stage 2 `AdminAgent`:

```python
from core.admin_agent import AdminAgent

def handle_user_reservation_intent(user_details: dict) -> str:
    """
    Called by Agent 1 when the user expresses clear reservation intent.
    """
    admin_agent = AdminAgent()
    
    request_id = admin_agent.escalate_reservation(
        user_name=user_details["name"],
        car_number=user_details["car_number"],
        period=user_details["period"]
    )
    
    if not request_id:
        return "I apologize, but I could not reach the facility administration at this time."
    
    is_approved = admin_agent.wait_for_approval(request_id)
    if is_approved:
        return f"Great news! Your reservation ({request_id}) has been approved by the parking administrator."
    else:
        return f"Your reservation request ({request_id}) could not be approved at this time."
```

---

## Roadmap

- [x] **Stage 1**: RAG Chatbot for Parking Space Regulations & Inquiries *(Completed)*
- [x] **Stage 2**: Human-in-the-Loop Admin Agent & Mock Admin Dashboard *(Current)*
- [ ] **Stage 3**: Real-time Database Integration & Slot Allocation Engine *(Pending)*
- [ ] **Stage 4**: Multi-Agent Supervisor & Autonomous Payment Gateway *(Pending)*

---

## License

This project is licensed under the terms of the [MIT License](https://opensource.org/licenses/MIT).
