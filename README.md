# Ashwin Logistics AI Support Agent

An authenticated logistics support API that combines shipment and customer records in MongoDB with internal policy documents indexed in Qdrant. A LangGraph workflow uses Azure OpenAI to choose tools, retrieve relevant data, and compose a response.

## What it does

- Authenticates users with MongoDB-backed bearer sessions.
- Keeps conversations, customers, bookings, and shipments scoped to their owner.
- Onboards customers and links their bookings and shipments.
- Answers shipment and customer questions using owner-scoped MongoDB tools.
- Retrieves internal policy and procedure content through Qdrant.
- Records account, session, conversation, and operational writes in an audit collection.

The project currently exposes a REST API; it does not include a web onboarding or chat interface.

## Request flow

```text
Client
  -> FastAPI authentication and owner context
  -> conversation history + LangGraph agent
  -> Azure OpenAI tool selection
  -> MongoDB customer/shipment tools or Qdrant policy retrieval
  -> Azure OpenAI response
  -> response with conversation/session IDs and X-Request-ID
```

## Stack

- Python 3.12+
- FastAPI and Pydantic
- MongoDB with the PyMongo async client
- LangGraph, LangChain, and Azure OpenAI
- Qdrant and Sentence Transformers for policy retrieval
- Pytest for automated tests

## Project layout

```text
app/
  ai/                 LangGraph workflow, model client, prompts
  api/                Routes, request models, bearer authentication
  config/             Environment-backed settings
  db/                 MongoDB collections and repositories
  models/             Conversation, user, and session models
  rag/                Document loading, chunking, embeddings, Qdrant retrieval
  tools/              Shipment, customer, and policy tools
data/
  documents/          Internal policy and support documents
  seed/               Sample customers, bookings, and shipments
scripts/              Database seeding and RAG setup scripts
tests/                Unit tests for authentication, ownership, and agent behavior
PHASE_9_AUTH_AND_CUSTOMER_ONBOARDING.md
PHASE_10_OBSERVABILITY.md
```

## Setup

Create `.env` from the provided template and configure MongoDB and Azure OpenAI:

```bash
cp .env.example .env
```

Set these values in `.env`:

| Variable | Purpose |
| --- | --- |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT` | Model/deployment name used by the agent |
| `MONGODB_URI` | MongoDB connection URI |
| `MONGODB_DATABASE` | Database name |
| `SEED_OWNER_PASSWORD` | Local seed admin password, at least 12 characters |
| `QDRANT_URL` | Optional; defaults to `http://localhost:6333` |
| `QDRANT_COLLECTION` | Optional; defaults to `ashwin_logistics_knowledge` |

The Azure OpenAI client uses `DefaultAzureCredential`; make an appropriate Azure credential available to the process. MongoDB is required at app startup because the app creates its collection indexes. Qdrant and the embedding model are needed when setting up or using policy retrieval.

Install dependencies with [uv](https://docs.astral.sh/uv/):

```bash
uv sync --dev
```

## Seed local data and prepare policy retrieval

The local seed owner is `ashwin@ashwinlogistics.com` with role `admin`. The seed script hashes `SEED_OWNER_PASSWORD` and upserts the owner and sample customer, booking, and shipment records. It does not store the plaintext password.

```bash
uv run python -m scripts.seed_mongodb
```

To use policy retrieval, start Qdrant, create the configured collection, and ingest the documents in `data/documents/`:

```bash
uv run python -m scripts.create_qdrant_collection
uv run python -m scripts.test_ingestion
```

## Run the API

```bash
uv run uvicorn app.main:app --reload
```

Interactive OpenAPI documentation is available at `http://127.0.0.1:8000/docs`. `GET /health` is public. All auth, chat, session, customer, booking, and shipment routes require `Authorization: Bearer <token>` except registration and login.

## Authentication and sessions

Register an operator account or log in. Both endpoints return an opaque bearer token and a session record:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"ashwin@ashwinlogistics.com","password":"<SEED_OWNER_PASSWORD>"}'
```

Use the returned `access_token` in the `Authorization` header. Tokens are stored as SHA-256 hashes. Passwords are stored as salted PBKDF2 hashes. Sessions expire after 12 hours; activity is recorded and `POST /sessions/refresh` extends the current session. Registration and login are limited to 10 attempts per source IP per minute per application process.

Public registration creates `operator` users. The seed script creates the local Ashwin account with the `admin` role. `POST /auth/logout` revokes the current session. `GET /auth/me`, `GET /sessions`, and `GET /sessions/{session_id}` return the current identity or that user's session records. A conversation is linked to its owner and the authenticated login session.

## API routes

All routes below require a valid bearer token unless marked public.

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Public service health check |
| `POST` | `/auth/register` | Public operator registration; creates a session |
| `POST` | `/auth/login` | Public login; creates a session |
| `POST` | `/auth/logout` | Revoke the current session |
| `GET` | `/auth/me` | Current user and session |
| `GET` | `/sessions` | List the current user's sessions |
| `GET` | `/sessions/{session_id}` | Get one owned session |
| `POST` | `/sessions/refresh` | Extend the current unexpired session |
| `POST` | `/ai/chat` | Send a message; optionally continue a conversation/session |
| `POST` | `/ai/chat/{conversation_id}` | Continue an owned conversation |
| `GET` | `/ai/conversations` | List the current user's conversations |
| `GET` | `/ai/conversations/{conversation_id}/history` | Read an owned conversation history |
| `POST` | `/customers` | Onboard a customer |
| `GET` | `/customers` | List owned customers |
| `GET` | `/customers/{customer_id}` | Get an owned customer |
| `PUT` | `/customers/{customer_id}` | Update an owned customer |
| `DELETE` | `/customers/{customer_id}` | Delete an owned customer without bookings |
| `POST` | `/bookings` | Create a booking for an owned customer |
| `GET` | `/bookings` | List owned bookings; optional `customer_id` filter |
| `GET` | `/bookings/{booking_id}` | Get an owned booking |
| `GET` | `/customers/{customer_id}/bookings` | List a customer's bookings |
| `POST` | `/shipments` | Create a shipment for an owned booking |
| `GET` | `/shipments` | List owned shipments; optional `customer_id` filter |
| `GET` | `/shipments/{shipment_id}` | Get an owned shipment |
| `GET` | `/customers/{customer_id}/shipments` | List a customer's shipments |

Example customer and booking creation:

```bash
TOKEN='<access_token>'

curl -X POST http://127.0.0.1:8000/customers \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Nisha Patel","email":"nisha@example.com","company":"Aster Labs","industry":"Pharma"}'

curl -X POST http://127.0.0.1:8000/bookings \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"customer_id":"<customer_id>","pickup_location":"Kochi","destination":"Dubai","service_type":"International Express"}'
```

Ownership is resolved from the bearer token, not a `user_id` supplied in the request body. Attempts to access another user's records return not found. Customer deletion is rejected while that customer has bookings.

## AI tools

- `get_shipment_status` retrieves shipment details only for the authenticated owner.
- `find_customer` searches that owner's customer names, email addresses, and companies.
- `get_customer_shipments` lists shipments for an owned customer.
- `search_internal_knowledge` retrieves relevant chunks from the configured Qdrant collection.

The graph routes tool calls through a LangGraph `ToolNode` and returns to the agent to compose the response. Tool and policy results are subject to the user's ownership scope where they access operational records.

## Logs, request IDs, and audit records

The API accepts an `X-Request-ID` header or generates one, logs incoming requests, and returns the ID in the response header. Chat responses also include `request_id`. Account, session, conversation, customer, booking, and shipment writes create MongoDB audit records. These features support traceability, but end-to-end traces and latency/token metrics are planned for Phase 10; see [PHASE_10_OBSERVABILITY.md](PHASE_10_OBSERVABILITY.md).

## Tests

Run the suite with:

```bash
uv run pytest -q
```

The tests cover password hashing and session validity, request validation, owner scoping, customer/booking/shipment routes, conversation ownership, and tool routing. They use mocks for MongoDB and model/tool calls; separate live-service checks are available under `scripts/`.

## Project roadmap

- **Phase 9 — Authentication and customer onboarding:** implemented.
- **Phase 10 — Observability:** planned in [PHASE_10_OBSERVABILITY.md](PHASE_10_OBSERVABILITY.md).
- Later work can add conversation summarization, approved operational write tools, deployment hardening, and Azure Monitor/Application Insights export.
