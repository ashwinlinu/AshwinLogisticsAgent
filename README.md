# Ashwin Logistics AI Support Agent

A logistics support assistant built to help support teams answer shipment-related questions quickly by combining policy documents, shipment data, and customer support history in one conversational workflow.

## Project Overview
Ashwin Logistics manages domestic and international shipments, and its support team currently works across multiple disconnected systems to answer customer questions. This project introduces an AI-powered agent to reduce manual work and provide consistent support responses.

The system is designed to help support agents answer questions such as:

- Where is shipment SHP-1042?
- Why is the shipment delayed?
- Can the shipment be cancelled?
- What policy applies to this case?
- What are the previous support issues for this customer?

## Business Goal
The primary goal is to create a unified AI support workflow that:

- Retrieves data from multiple systems
- Uses internal policy documents for decision support
- Combines operational data and customer context
- Provides accurate, policy-grounded responses
- Supports safe operational actions like ticket creation and escalation

## Core Features
### 1. Internal Knowledge Retrieval
The agent can search internal documentation and policy files to answer policy-driven questions.

### 2. Shipment Information Lookup
The agent can query shipment data through a simulated REST API to get delivery status, current location, expected date, and delay reason.

### 3. Customer and Support History Lookup
The agent can fetch customer records and support history from MongoDB to explain prior issues and context.

### 4. Multi-Source Reasoning
The agent combines shipment data, customer history, and policy rules to answer complex questions in a single response.

### 5. Safe Action Support
The agent can support actions such as creating support tickets or escalating issues, with safeguards to prevent accidental or unauthorized operations.

## Architecture
The solution is built around a modular orchestration pattern:

- LangGraph for workflow orchestration
- Azure OpenAI for reasoning and response generation
- Qdrant for vector retrieval from company documents
- MongoDB for customer and support-related records
- Shipment REST API as the source of shipment details

### High-Level Flow
User request
  -> LangGraph workflow
  -> Tool selection
  -> Data retrieval from docs / API / database
  -> AI reasoning and synthesis
  -> Final response or action

## Example Use Cases
- "Where is my shipment SHP-1042?"
- "Why is it delayed and what should I tell the customer?"
- "Can we cancel the shipment?"
- "Show the customer’s previous support issues."
- "Create a high-priority support ticket for SHP-1042."

## Project Structure
```text
Logistics_agent/
├── README.md
├── requirement_doc.md
├── main.py
├── pyproject.toml
└── data/
    └── documents/
```

## Tech Stack
- Python
- LangGraph
- Azure OpenAI
- Qdrant
- MongoDB
- REST API integration

## Setup
1. Create and activate a Python virtual environment.
2. Install project dependencies.
3. Configure environment variables for Azure OpenAI, MongoDB, and other services.
4. Load synthetic policy documents and seed sample customer/shipment data.
5. Run the application using the Python entry point.

## Running the Project
```bash
python main.py
```

## Authentication and customer onboarding

Protected API routes use opaque bearer tokens backed by MongoDB sessions. Register an operator account with `POST /auth/register` (passwords must be at least 12 characters), or log in with `POST /auth/login`. Send the returned token as `Authorization: Bearer <token>`. `POST /auth/logout` revokes the current session; sessions expire after 12 hours and can be extended with `POST /sessions/refresh`. Conversations are bound to both their owner and the authenticated session, so separate logins do not share conversational history.

The seeded local admin account uses `ashwin@ashwinlogistics.com`. Set `SEED_OWNER_PASSWORD` (at least 12 characters) before running `python -m scripts.seed_mongodb`; the seed script stores only a password hash and adds owner IDs to customers, bookings, and shipments. Customer, booking, shipment, and conversation queries are scoped to the authenticated user's `user_id`. Public registration creates operator accounts; the local seeded account is the admin. Account, session, conversation, and operational writes create audit records. Registration and login are throttled to 10 requests per source IP per minute per app process.

Customer onboarding uses `POST /customers`; bookings are created with `POST /bookings` referencing an owned `customer_id`, and shipments with `POST /shipments` referencing an owned `booking_id`. List and detail routes are also owner scoped.

## Current Status
This is a project foundation and architecture specification for an enterprise AI support agent. The next phase typically includes:

- Document ingestion and indexing
- Tool-based retrieval workflows
- Shipment API integration
- MongoDB data access
- LangGraph orchestration
- Testing and validation scenarios

## Future Improvements
- Role-based access control
- Human approval for write actions
- Monitoring and observability
- Expanded logistics operations workflows
- Better support ticket automation

## Final Recommendations

The project is now in a strong Phase 8 state, but these are the next production improvements I recommend:

1. Add explicit session creation and session management APIs
   - `POST /ai/sessions`
   - `GET /ai/sessions/{session_id}`
   - `GET /ai/sessions/{session_id}/history`

2. Add auth and user identity handling
   - Replace the hardcoded `ashwinlinu` user with a real identity provider or login layer.
   - Store `user_id` and `session_id` in a secure session store.

3. Add observability and tracing
   - structured logs per request
   - latency metrics
   - error tracking / Sentry or equivalent
   - correlation IDs across downstream tool calls

4. Add database migrations and schema versioning
   - conversation stores should be versioned
   - ensure collection indexes are created for `user_id`, `conversation_id`, and `session_id`

5. Add more end-to-end API tests with TestClient
   - chat endpoints
   - conversation history endpoints
   - shipment lookup errors
   - validation failures

6. Add a light context summarization layer
   - long conversations should be summarized to avoid context bloat.
   - keep the latest shipment ID and key customer context in memory/state.

7. Add permissions and safe actions
   - human approval for write-like operations
   - role-based access for operational actions
   - audit trail for all support actions

8. Add deployment and environment hardening
   - separate dev/staging/prod config
   - secret management
   - health checks and readiness probes
   - startup validation for Mongo/Qdrant/OpenAI connectivity

## Recommended Next Milestones

- Phase 9: Real user auth and session management
- Phase 10: Conversation summarization and context retention
- Phase 11: Operational write tools and approval workflows
- Phase 12: Monitoring, deployment hardening, and production readiness review

## Summary
The goal of this project is to reduce support handling time and improve customer response quality by building an AI support assistant that can reason across policy, operational data, and customer records in a single workflow.
