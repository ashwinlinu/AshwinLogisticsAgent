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

## Summary
The goal of this project is to reduce support handling time and improve customer response quality by building an AI support assistant that can reason across policy, operational data, and customer records in a single workflow.
