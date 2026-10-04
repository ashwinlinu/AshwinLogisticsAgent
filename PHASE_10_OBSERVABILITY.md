# Phase 10 — Observability

**Status:** Planned

## Objective

Make the full request path visible and measurable so developers can answer:

- How long did an API request take?
- Which part of the AI workflow caused the delay or failure?
- How often are the LLM, retrieval, tools, and MongoDB used?
- How many tokens did a model call consume?
- Can one request be followed from the API through the agent and its tools?

The implementation should begin with provider-neutral instrumentation and leave a clear path to OpenTelemetry export through Azure Monitor or Application Insights. It should add useful signals without coupling core application code to a single monitoring vendor.

## Business Goal

Give the project an observable, explainable AI workflow suitable for operating and demonstrating an AI Engineer / FDE portfolio project. When an answer is slow, wrong, or unavailable, the team should be able to find the responsible stage without logging customer messages or exposing credentials.

## Current Baseline

- The HTTP middleware accepts or creates an `X-Request-ID`, logs the incoming route, and returns the ID in the response header.
- Chat responses include the request ID.
- Some tool failures are logged, but logs do not consistently share request or trace context.
- The AI graph calls the model in the agent node, dispatches MongoDB or RAG tools, and calls the agent again to synthesize tool results.
- RAG embeds the query and calls Qdrant. Shipment and customer tools query MongoDB.
- Business write audit records are stored separately in MongoDB `audit_logs`; these are not performance telemetry.
- The app does not yet emit end-to-end traces, latency histograms, token metrics, or centralized telemetry.

The graph and request flow to instrument are:

```text
HTTP request
  -> authentication / request context
  -> conversation lookup and history
  -> LangGraph agent
       -> Azure OpenAI model call
       -> tool dispatch
            -> MongoDB shipment/customer query
            -> or RAG embedding -> Qdrant query
       -> Azure OpenAI response call
  -> conversation persistence
  -> HTTP response
```

## Core Requirements

### 1. Correlated request and trace context

- Preserve the existing `X-Request-ID` behavior.
- Create or continue a distributed trace for each HTTP request, honoring standard W3C trace context when supplied.
- Propagate trace context through the AI service, LangGraph nodes, model calls, tools, MongoDB operations, and Qdrant retrieval.
- Include the request/trace ID in structured logs and error responses where appropriate.
- Do not use request IDs, user IDs, customer IDs, shipment IDs, or conversation IDs as metric labels; they create high-cardinality metrics. Keep IDs in traces/logs where access is controlled.

### 2. Latency and request metrics

Record at least:

- API request count, total duration, and response status.
- End-to-end chat duration.
- LLM call duration, separated by operation/model where available.
- MongoDB operation duration for auth/session, conversation, customer, booking, and shipment queries.
- RAG duration, with embedding and Qdrant query timing where practical.
- Tool invocation duration and invocation count by tool name.

Use histograms for durations and counters for counts/errors. Keep metric dimensions low cardinality, such as route template, method, status class, tool name, and error category.

### 3. AI usage and outcome metrics

- Capture prompt, completion, and total token usage when the model response provides it.
- Count LLM calls and tool calls per request/trace.
- Count RAG retrievals and record returned-result count, without recording document text.
- Track tool errors, model errors/timeouts, retrieval errors, and failed HTTP requests separately.
- Distinguish an expected tool result such as `not_found` from an infrastructure failure.
- Record whether a request completed, used a fallback answer, or failed, because the AI service currently has fallback behavior that may not map to an HTTP 500.

### 4. Structured logs and error context

- Emit structured logs with timestamp, severity, service name, environment, request ID, trace ID, operation, duration, and normalized outcome/error type.
- Keep logs useful for local development and compatible with future Azure Monitor ingestion.
- Record stack traces for unexpected failures while keeping API responses free of internal details.
- Avoid logging passwords, bearer tokens, authorization headers, raw customer contact data, full prompts, model outputs, or retrieved document content.

### 5. Provider-neutral instrumentation

- Keep instrumentation behind a small application telemetry module or standard OpenTelemetry APIs.
- Make local development useful without requiring an Azure subscription or hosted collector.
- Export to a local console or configurable OTLP endpoint during development.
- Add Azure Monitor/Application Insights as an optional exporter/configuration target after the telemetry and privacy behavior is validated.
- Keep monitoring outages from breaking API requests; exporter errors should be reported safely and must not interrupt business operations.

## Proposed Trace Shape

Each chat request should produce a trace resembling:

```text
http.server POST /ai/chat
  ├─ auth.resolve_identity
  ├─ conversation.load_or_create
  ├─ conversation.load_history
  ├─ ai.graph.invoke
  │    ├─ ai.agent
  │    │    └─ gen_ai.client.inference
  │    ├─ ai.tool.invoke [tool name]
  │    │    ├─ db.query [MongoDB tool] 
  │    │    └─ rag.retrieve
  │    │         ├─ embeddings.create
  │    │         └─ db.query [Qdrant]
  │    └─ ai.agent / gen_ai.client.inference [final response]
  ├─ conversation.persist_messages
  └─ http.response
```

Not every request uses a tool. A conversation may call the agent/model more than once when it first requests a tool and then synthesizes the tool result; each model call should have its own span and token data.

## Proposed Metrics

| Metric | Type | Suggested attributes |
| --- | --- | --- |
| `http.server.request.count` | Counter | method, route template, status code |
| `http.server.request.duration` | Histogram | method, route template, status class |
| `ai.chat.duration` | Histogram | outcome |
| `gen_ai.client.operation.duration` | Histogram | operation, model/deployment |
| `gen_ai.client.token.usage` | Counter | token type, model/deployment |
| `ai.tool.invocations` | Counter | tool name, outcome |
| `ai.tool.duration` | Histogram | tool name, outcome |
| `rag.retrieval.count` | Counter | outcome |
| `rag.retrieval.duration` | Histogram | outcome |
| `rag.retrieval.results` | Histogram | bounded result count |
| `db.client.operation.duration` | Histogram | database system, operation, collection |
| `app.errors` | Counter | component, normalized error category |

Names are illustrative; use stable OpenTelemetry semantic conventions where applicable instead of inventing parallel names. Avoid attributes whose values are unique per request or customer.

## Proposed Configuration

Add optional settings only when the instrumentation is implemented. Names may follow the OpenTelemetry SDK conventions, for example:

```env
OTEL_SERVICE_NAME=ashwin-logistics-agent
OTEL_RESOURCE_ATTRIBUTES=deployment.environment=development
OTEL_TRACES_EXPORTER=console
OTEL_METRICS_EXPORTER=console
OTEL_EXPORTER_OTLP_ENDPOINT=
OBSERVABILITY_ENABLED=true
```

Exact configuration should follow the chosen OpenTelemetry Python packages. Azure Monitor connection strings or credentials must remain secret configuration and must not be committed to `.env.example` with real values.

## Proposed Milestones

### Milestone 1 — Observability design and safe context

Tasks:

- Define service/resource attributes for app name, version, and environment.
- Preserve request IDs and add trace-context extraction/injection.
- Define normalized outcome and error categories for API, agent, model, tools, MongoDB, and RAG.
- Document sensitive fields and redaction rules.

Acceptance criteria:

- A request can be correlated across logs and trace context.
- IDs are not used as metric dimensions.
- Secrets and user content are excluded from telemetry by default.

### Milestone 2 — HTTP and application traces

Tasks:

- Add server spans for incoming requests and response status.
- Add spans around chat generation, conversation reads/writes, and authentication/session lookups.
- Record API and chat request counts, outcomes, and durations.
- Preserve the existing request-ID response header.

Acceptance criteria:

- Local requests produce a trace with an HTTP root span and relevant child spans.
- Request duration and response outcome are measurable for both successful and failed requests.

### Milestone 3 — LLM instrumentation

Tasks:

- Add spans around every Azure OpenAI request.
- Capture model/deployment, duration, outcome, and token usage when returned by the SDK.
- Record timeout, authentication, rate-limit, and provider error categories.
- Ensure prompts, completions, and credentials are not included in telemetry.

Acceptance criteria:

- Each model call can be distinguished within a trace.
- Token and latency metrics are recorded when provider metadata exists; missing usage metadata is handled safely.

### Milestone 4 — Tool, MongoDB, and RAG instrumentation

Tasks:

- Instrument tool selection/invocation and distinguish tool-level results from tool exceptions.
- Record MongoDB query operation duration by safe operation/collection attributes.
- Instrument embedding and Qdrant retrieval separately and as a total RAG operation.
- Record retrieval result count and failures without storing retrieved content.

Acceptance criteria:

- A trace shows which tool ran and its duration/outcome.
- Shipment/customer MongoDB access and RAG retrieval can be distinguished.
- Tool invocation counts, tool errors, and RAG counts are available.

### Milestone 5 — Metrics export and local development

Tasks:

- Configure provider-neutral OpenTelemetry APIs/SDK and metric instruments.
- Provide a local console or OTLP development exporter.
- Add bounded-cardinality metric attributes and document a local inspection workflow.
- Ensure telemetry initialization and shutdown/flush are safe and optional.

Acceptance criteria:

- Developers can inspect traces and metrics locally without Azure Monitor.
- Disabling or losing the exporter does not make API requests fail.

### Milestone 6 — Azure Monitor/Application Insights integration

Tasks:

- Add Azure Monitor/Application Insights exporter as an optional deployment integration.
- Configure service/environment resource attributes and connection settings through environment configuration.
- Document how to find a request trace, latency breakdown, token usage, and tool errors in the monitoring UI.
- Validate redaction and sampling before enabling production export.

Acceptance criteria:

- An authorized deployment can export traces and metrics to Azure Monitor.
- The same application instrumentation works with local and Azure exporters.
- No secrets or raw customer conversation content are exported.

## Security, Privacy, and Cost Guardrails

- Never emit passwords, access tokens, authorization headers, email addresses, phone numbers, full prompts, full completions, or policy document content.
- Use IDs in trace/log context only where needed and protect access to telemetry stores; do not attach these IDs to metrics.
- Consider sampling for high-volume traces while preserving errors and slow requests.
- Bound dimensions and label values to prevent cardinality and storage-cost growth.
- Configure exporter timeouts and batch limits so a telemetry backend outage cannot block application work.
- Keep the MongoDB `audit_logs` collection for business-change auditability; use traces and metrics for runtime behavior.

## Implementation Order

1. Agree on trace boundaries, metric names, error categories, and redaction behavior.
2. Add request trace context and structured logging fields.
3. Instrument HTTP, conversation persistence, and AI workflow duration/outcome.
4. Instrument LLM calls, tokens, tools, MongoDB operations, and RAG retrieval.
5. Add tests for trace propagation, metric recording, failures, and telemetry-offline behavior.
6. Add local exporter instructions and verify a complete sample trace.
7. Add optional Azure Monitor export and deployment configuration.

## Acceptance Criteria for This Phase

- A chat request can be followed from HTTP ingress through agent, model, tool/RAG, and response.
- Total, LLM, retrieval, MongoDB, and tool latencies are measurable.
- Tool invocation count, token usage, failed requests, RAG retrieval count, and tool errors are recorded.
- Errors distinguish application/model/tool/retrieval/database failures and expected not-found outcomes.
- Request IDs and trace context correlate logs and spans without high-cardinality metrics.
- Telemetry excludes secrets and raw user/customer content.
- Local development can inspect telemetry without a cloud account.
- Azure Monitor/Application Insights can be enabled later through optional configuration without rewriting application instrumentation.
- Automated tests verify successful traces, failure outcomes, token metadata handling, and exporter failure isolation.

## Out of Scope

- Replacing business audit records or storing chat transcripts in the telemetry backend.
- Building dashboards and alert policies for every metric in this phase; provide a small useful starter view after instrumentation works.
- Making telemetry export mandatory for local development or API availability.
- Logging prompts or responses to simplify debugging.

## Next Phase

After observability is in place, later work can add deployment dashboards/alerts, conversation summarization, approved operational actions, and production readiness controls using the collected runtime signals.
