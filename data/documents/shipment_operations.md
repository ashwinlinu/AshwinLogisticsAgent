---
document_id: shipment-operations-v1
title: Shipment Operations Handbook
category: operations
version: "1.0"
source: "internal"
effective_date: "2026-01-01"
---

# Shipment Operations Handbook

## Purpose

This handbook defines the operational workflow for Ashwin Logistics shipments from booking through final delivery. It is intended to standardize shipment lifecycle handling, support escalation, and exception management across domestic and international freight operations.

Ashwin Logistics handles road freight, air freight, sea freight, warehousing, and distribution. Every shipment is tracked using a unique Shipment ID in the format SHP-XXXX and a booking reference in the format BKG-XXXX. Examples include SHP-1001, SHP-1002, and BKG-2001.

For claims related to cargo damage, loss, shortage, or service failure, Ashwin Logistics internal policy requires that claims must normally be reported within 7 calendar days of delivery or discovery of the incident.

## Shipment Lifecycle and Status Model

The standard shipment lifecycle across Ashwin Logistics is:

BOOKED → PICKUP_SCHEDULED → PICKED_UP → IN_TRANSIT → AT_ORIGIN_FACILITY → AT_DESTINATION_FACILITY → OUT_FOR_DELIVERY → DELIVERED

Exception and recovery states are:

- DELAYED
- EXCEPTION
- CUSTOMS_HOLD
- CANCELLED
- RETURNED

### Status Reference Table

| Status | Meaning | Operational action |
| --- | --- | --- |
| BOOKED | Booking is accepted and allocated to a lane, route, or service level. | Confirm pickup schedule, collect required documents, prepare customer communication. |
| PICKUP_SCHEDULED | Pickup has been assigned to a vehicle or carrier partner. | Validate pickup window and address; monitor for no-show or late pickup. |
| PICKED_UP | Shipment has been accepted by the carrier or warehouse team. | Begin transit tracking and document collection. |
| IN_TRANSIT | Shipment is moving through the transport network. | Monitor milestones, route adherence, and ETA risks. |
| AT_ORIGIN_FACILITY | Shipment arrived at origin handling point or consolidation hub. | Check for sorting, scanning, or documentation issues. |
| AT_DESTINATION_FACILITY | Shipment arrived at destination facility and is awaiting final movement. | Confirm readiness for delivery or customs clearance. |
| OUT_FOR_DELIVERY | Final-mile vehicle has been assigned. | Confirm delivery window and customer contact. |
| DELIVERED | Shipment reached the final delivery destination and was accepted. | Close operational milestones and document any claim or exception. |
| DELAYED | Shipment movement is behind plan due to weather, lane constraints, or operational disruption. | Notify relevant stakeholders and escalate if customer impact exceeds threshold. |
| EXCEPTION | Shipment has a service or process exception requiring investigation. | Initiate reroute, hold, recovery, or customer communication based on issue type. |
| CUSTOMS_HOLD | Shipment cannot proceed through customs until required documentation or clearance actions are completed. | Validate forms, work with compliance team, and update customer timeline. |
| CANCELLED | Booking is cancelled before shipment movement. | Apply cancellation policy and document reason and approval status. |
| RETURNED | Shipment is being returned to sender or origin due to refusal, failed delivery, or operational exception. | Follow return workflow and customer notification process. |

## Booking to Pickup Process

A shipment begins when a customer request is accepted and assigned a booking reference such as BKG-2001. The booking must include customer details, origin and destination locations, commodity description, service type, requested pickup date and time, and any special handling instructions.

After booking confirmation, the operations team validates service eligibility, transit lead time, and vehicle availability. If all conditions are met, the shipment progresses to PICKUP_SCHEDULED. If a pickup cannot be completed as planned, the shipment may move to EXCEPTION or DELAYED depending on the cause.

### Pickup Failure and Recovery

A failed pickup is defined as a carrier or service partner not collecting the shipment within the agreed pickup window or a customer not making the shipment available at the scheduled time. In these situations:

1. The assigned operations coordinator records the reason for the failed pickup.
2. Support checks the latest shipment status and informs the customer of the operational delay.
3. Operations evaluates whether the pickup can be rescheduled, reassigned, or converted to a priority move.
4. If a shipment remains uncollected beyond the service standard, the issue is escalated to L2.

If the pickup failure is caused by missing or incorrect documentation, the shipment may be held in EXCEPTION until the required documents are corrected.

## Transit, Facility, and Delivery Process

Once the shipment is picked up, it moves to IN_TRANSIT. During transit, Ashwin Logistics monitors route progress, vehicle status, handoffs, and delivery milestones. A delay may be recorded as DELAYED when planned ETAs cannot be met because of weather, route disruption, equipment failure, or network backlog.

When a shipment reaches an origin or destination consolidation facility, it moves to either AT_ORIGIN_FACILITY or AT_DESTINATION_FACILITY. These states are operationally important because they often signal a handoff, sorting event, or final movement readiness check.

The destination facility process includes:

- scanning the shipment on arrival
- verifying the destination address, reference number, and handling instructions
- checking whether customs documentation is complete
- preparing the shipment for final sorting and dispatch

A shipment enters OUT_FOR_DELIVERY when a final-mile carrier is assigned and the vehicle is dispatched for doorstep delivery.

### Failed Delivery and Return Handling

A failed delivery occurs when the final-mile carrier cannot complete the delivery due to no-access, incorrect address details, customer unavailable, or refusal. The shipment is generally placed in EXCEPTION or RETURNED depending on the reason and whether the shipment is being redirected or returned to origin.

For failed delivery scenarios, operations reviews whether:

- the delivery should be reattempted
- the shipment requires a new delivery appointment
- the shipment should be returned to origin
- a customer notification and escalation are required

If the shipment is returned, the status becomes RETURNED. Return handling follows the return/exception workflow rather than normal cancellation logic because the shipment has already been picked up.

## Customs Hold and Compliance Interaction

A shipment may enter CUSTOMS_HOLD when the documentation required for cross-border movement is incomplete, incorrect, or pending regulatory clearance. This status means the shipment cannot proceed through the applicable customs process until the required documentation or clearance action is completed.

Common causes of CUSTOMS_HOLD include missing commercial invoice details, inconsistent declared value, incomplete packing list, missing permits, or incomplete customs declarations. The compliance team and freight operations coordinate to resolve the hold, while support provides customer updates based on verified operational status.

## Escalation Model

Ashwin Logistics uses three support escalation levels:

- L1 — Customer Support: basic shipment questions, status interpretation, documentation questions, routine booking questions.
- L2 — Operations: delayed shipments, failed pickups, routing issues, shipment exceptions, operational intervention.
- L3 — Specialist / Management: major customer-impacting incidents, high-value shipment issues, repeated service failures, serious claims, compliance issues, unresolved L2 escalations.

A case moves to L2 when there is an operational disruption or route issue that cannot be resolved through standard support processes. A case moves to L3 when the issue threatens major customer impact, involves repeated failures, serious claims, or unresolved compliance concerns.

Examples include:

- A customer asks for a shipment status update: L1.
- A shipment is marked DELAYED for more than 24 hours without a recovery plan: L2.
- A shipment remains in CUSTOMS_HOLD because of incomplete customs paperwork for several business days: L3.
- A high-value shipment is repeatedly missed across multiple attempted pickups: L3.

## Common Questions Answered by This Document

- What does BOOKED mean?
- What is the standard shipment lifecycle at Ashwin Logistics?
- What does CUSTOMS_HOLD mean?
- When does a shipment move from IN_TRANSIT to AT_DESTINATION_FACILITY?
- What should happen when a pickup fails?
- What is the difference between DELAYED and EXCEPTION?
- What does OUT_FOR_DELIVERY mean?
- When should a delayed shipment be escalated to Operations?
- What is the correct handling for a failed delivery?
- When does a shipment move to RETURNED status?
