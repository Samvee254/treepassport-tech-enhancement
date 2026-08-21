# Audit Trail — Design

## Purpose
Provide a tamper-evident, immutable record of changes to tree data, so
any edit can be traced to who made it, when, and what changed.

## AuditLog entry structure
- id             (unique identifier)
- tree_id        (which tree record changed)
- user_id        (who made the change)
- field_changed  (e.g. "location", "health_status")
- old_value
- new_value
- timestamp
- action_type    (CREATE / UPDATE / VERIFY / FLAG)
- flagged        (boolean - did this change trigger a review?)

## Core principle
Every change produces a new, immutable log entry rather than overwriting
history. The tree record shows the current state; the audit log shows
how it got there.

## Flagging logic

Sensitive fields (any change auto-flags for review):
- GPS coordinates (location)
- Verification status
- Species

Non-sensitive fields (logged, not auto-flagged):
- Health status (expected to change naturally over time)
- Growth measurements
- Photos

Rationale: logging everything is necessary but not sufficient - flagging
only sensitive-field changes avoids alert fatigue while still catching
the changes most likely to indicate error or tampering (e.g. a tree's
location silently moving from Machakos to Nairobi).

## Example event

    Location changed
    User: Field Officer 04
    Tree ID: TP-KEN-2026-000123
    Previous: Machakos
    New: Makueni
    Time: 2026-08-19 14:32
    Action: UPDATE
    Flagged: TRUE (sensitive field)

## Explicit distinction
This audit/flagging system is a proposed enhancement. TreePassport's
existing platform is not known to include this level of change tracking;
this design demonstrates how it could be added.

## Revision: bug found during testing (monitoring-record audit logging)

When audit logging was added to monitoring-record creation, the first
implementation used the newly-created record's own height as the
"old_value" instead of the previous record's height - meaning old and
new values were identical or misleading in the log. This was caught by
testing the actual output rather than assuming the log was correct, and
fixed by querying the previous monitoring record before inserting the
new one. This is now correctly reflected in the audit log: old_value
captures the tree's state before the check-in, new_value captures the
state after.
