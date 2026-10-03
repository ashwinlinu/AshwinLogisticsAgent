# Phase 9 — Authentication, User Session Management, and Customer Onboarding

## Objective

Replace the hardcoded `ashwinlinu` assumption with a proper ownership model for the logistics app, where:

- the primary user is the app owner/admin
- login is personal and authenticated
- each user gets their own session history and identity
- customer onboarding is part of the workflow
- shipments and bookings are linked to the correct customer and owner
- future multi-user or team-based access can be added without rewriting the system

This is the next logical step after the Phase 8 API cleanup and the Phase 7 conversation persistence work.

## Business Goal

The product should support a single primary business user, Ashwin, who can:

- log in with their own credentials
- manage their own active sessions
- onboard customers into the system
- add bookings and shipments for those customers
- track shipments, bookings, and support conversations per customer
- keep a clean record of their own operational ownership

## Core Requirements

### 1. User identity and login

We need a real user model with:

- `user_id`
- `email`
- `password_hash` or a secure auth mechanism
- `full_name`
- `role` (admin / operator / support)
- `created_at`
- `updated_at`
- `status`

This should live in a Mongo collection such as `users`.

### 2. Session management

We need a session record with:

- `session_id`
- `user_id`
- `created_at`
- `expires_at`
- `last_activity_at`
- `is_active`

The app should use session-based identity rather than relying on a hardcoded fallback.

### 3. Per-user conversation ownership

Every conversation should be owned by the logged-in user:

- `conversation_id`
- `session_id`
- `user_id`
- `messages`
- `status`
- `created_at`
- `updated_at`

Understanding and reuse should be scoped to the user, not to a global default.

### 4. Customer onboarding

We need a `customers` collection with:

- `customer_id`
- `user_id` (owner/creator)
- `name`
- `email`
- `phone`
- `company`
- `industry`
- `address`
- `status`
- `created_at`

This lets Ashwin onboard multiple customers while keeping them connected to his account.

### 5. Booking and shipment relationships

We need a strong object graph:

- a customer can have many bookings
- a booking can have one or many shipments
- a shipment belongs to a booking and a customer
- a conversation can reference a shipment or customer context

Suggested schema fields:

- `bookings`: `booking_id`, `customer_id`, `user_id`, `shipment_ids[]`, `status`, `pickup_location`, `destination`, `created_at`
- `shipments`: `shipment_id`, `customer_id`, `booking_id`, `user_id`, `status`, `origin`, `destination`, `carrier`, `estimated_delivery`, `last_update`, `updated_at`

## Proposed Data Model

### users

```json
{
  "user_id": "USR-1001",
  "email": "ashwin@ashwinlogistics.com",
  "password_hash": "***hashed***",
  "full_name": "Ashwin",
  "role": "admin",
  "status": "active",
  "created_at": "2026-10-03T00:00:00Z"
}
```

### sessions

```json
{
  "session_id": "sess_abc123",
  "user_id": "USR-1001",
  "created_at": "2026-10-03T10:00:00Z",
  "last_activity_at": "2026-10-03T10:45:00Z",
  "expires_at": "2026-10-03T12:00:00Z",
  "is_active": true
}
```

### customers

```json
{
  "customer_id": "CUS-3001",
  "user_id": "USR-1001",
  "name": "Nisha Patel",
  "email": "nisha.patel@example.com",
  "phone": "+91 98765 43210",
  "company": "Aster Labs",
  "industry": "Pharma",
  "address": "Bengaluru",
  "status": "active",
  "created_at": "2026-10-01T09:00:00Z"
}
```

### bookings

```json
{
  "booking_id": "BKG-2001",
  "user_id": "USR-1001",
  "customer_id": "CUS-3001",
  "shipment_id": "SHP-1001",
  "status": "confirmed",
  "pickup_location": "Kochi",
  "destination": "Dubai",
  "service_type": "International Express",
  "created_at": "2026-10-01T10:00:00Z"
}
```

### shipments

```json
{
  "shipment_id": "SHP-1001",
  "user_id": "USR-1001",
  "customer_id": "CUS-3001",
  "booking_id": "BKG-2001",
  "status": "IN_TRANSIT",
  "origin": "Kochi",
  "destination": "Dubai",
  "carrier": "Ashwin Logistics",
  "pickup_date": "2026-10-01",
  "estimated_delivery": "2026-10-05",
  "last_update": "Shipment departed Kochi facility",
  "updated_at": "2026-10-01T08:30:00Z"
}
```

## Proposed Milestones

### Milestone 1 — User authentication foundation

Tasks:

- create `users` collection and repository
- define `User` model
- create password hashing strategy
- create auth login endpoint
- create user registration endpoint
- create `GET /me` endpoint

Acceptance criteria:

- a user can register with email/password
- password is stored securely
- a logged-in user can be resolved from a session token or auth context

### Milestone 2 — Session allocation and session records

Tasks:

- create `sessions` collection
- generate session IDs on login
- attach session to user
- enforce expiry/refresh on activity
- create logout endpoint

Acceptance criteria:

- each login creates one active session
- session history is tracked in MongoDB
- expired sessions are no longer valid

### Milestone 3 — Replace hardcoded user routing

Tasks:

- remove `ashwinlinu` default fallback from business logic
- resolve the current user from auth/session context
- bind conversations, bookings, and messages to `user_id`
- keep `ashwinlinu` as a seed user for local development only

Acceptance criteria:

- no route depends on a hardcoded user
- every conversation is linked to a real user
- the user identity is always available inside the request context

### Milestone 4 — Customer onboarding

Tasks:

- add `customers` collection and repository
- build onboarding form and API payload
- create `POST /customers`
- create `GET /customers`
- create `GET /customers/{customer_id}`
- create update/delete flows for admin use

Acceptance criteria:

- Ashwin can onboard new customers
- customers are linked to the current user
- customer records are stored in MongoDB

### Milestone 5 — Bookings and shipments relationship layer

Tasks:

- seed sample bookings data
- seed sample customer records
- connect bookings to customers
- connect shipments to bookings and customers
- create inventory-like queries for shipments by customer and user

Acceptance criteria:

- each booking references a customer and owner user
- each shipment references a customer and booking
- the app can list customers and shipments for the current user

### Milestone 6 — Intelligent customer support workflow

Tasks:

- attach customer context to chat context
- allow the agent to answer with customer-specific data
- allow shipment lookup using customer-owned records
- support “Who is this customer?” and “What shipments does this customer have?”

Acceptance criteria:

- the agent can reason using customer, booking, and shipment metadata
- the user can manage a customer’s shipments and support issues in one flow

### Milestone 7 — Security and production guardrails

Tasks:

- validate password strength
- add session expiry
- add rate limiting
- add audit logs
- restrict customer access by user ownership

Acceptance criteria:

- no user can access another user’s customers or bookings
- all writes are logged
- sensitive data is not exposed across tenant/user boundaries

## Recommended API Surface

### Authentication

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`

### Session

- `GET /sessions`
- `GET /sessions/{session_id}`
- `POST /sessions/refresh`

### Customers

- `POST /customers`
- `GET /customers`
- `GET /customers/{customer_id}`
- `PUT /customers/{customer_id}`
- `DELETE /customers/{customer_id}`

### Bookings

- `POST /bookings`
- `GET /bookings`
- `GET /bookings/{booking_id}`
- `GET /customers/{customer_id}/bookings`

### Shipments

- `POST /shipments`
- `GET /shipments`
- `GET /shipments/{shipment_id}`
- `GET /customers/{customer_id}/shipments`

### Chat

- `POST /ai/chat`
- `POST /ai/chat/{conversation_id}`
- `GET /ai/conversations`
- `GET /ai/conversations/{conversation_id}/history`

## Dummy Data to Seed for Local Development

We should seed the database with a realistic sample owner and customer base for Ashwin.

### Default primary user

```json
{
  "user_id": "USR-1001",
  "email": "ashwin@ashwinlogistics.com",
  "full_name": "Ashwin",
  "role": "admin"
}
```

### Seed customers

Use the existing `data/seed/customers.json` with sample records for:

- Nisha Patel
- Rohan Menon
- Meera Shah

### Seed bookings

Use the existing `data/seed/bookings.json` with sample records that point to those customers and shipments.

### Seed shipments

Use the existing `data/seed/shipments.json` as already populated for the sample flows.

## Implementation Order

1. Define user and session collections and repositories
2. Implement auth/login/register endpoints
3. Replace hardcoded user fallback
4. Attach user ownership to conversations
5. Create customer onboarding endpoints
6. Create booking and shipment association endpoints
7. Build agent context from current user + customer + shipment data
8. Add strong tests for access control and session validity
9. Add security hardening and audit logging

## Acceptance Criteria for This Phase

- a real user can sign in
- a real session is created and stored in MongoDB
- conversations are linked to the logged-in user
- customers can be onboarded and linked to a user
- bookings are linked to a customer and owner
- shipments are linked to customer and booking records
- there are realistic seed records in `customers.json` and `bookings.json`
- tests confirm that user ownership is respected across customer and shipment access

## Notes

This is the correct next phase because it reorients the system from a demo app to a proper owner-driven operations platform. It also creates the data model needed for future support operations, onboarding, session recovery, and per-user access rules.

Once this is in place, we can add more advanced features like customer profile tools, booking creation, shipment updates, and approval flows without breaking the architecture.
