# System Architecture

## High-level flow

    Frontend (React)
          |
       REST API (FastAPI)
          |
    Authentication / Authorization (JWT, role-based)
          |
    Business Logic Layer
          |
    Database (PostgreSQL)

## Business logic layer components

    - Tree Service        (CRUD for tree records)
    - Monitoring Service   (create check-ins, fetch history)
    - Risk Engine Service  (reads monitoring_records, computes score)
    - Audit Service        (intercepts writes, logs changes, flags sensitive edits)
    - Report Service       (aggregates data -> PDF/CSV)

## Request flow example: updating a tree's GPS location

    1. Field officer submits update via frontend
    2. API validates JWT + role (field_officer or admin only)
    3. Tree Service receives update request
    4. Audit Service intercepts BEFORE the write:
         - captures old_value
         - captures new_value
         - field_changed = "gps_lat" / "gps_lng"
         - since these are sensitive fields -> flagged = true
    5. Write is committed to trees table
    6. audit_logs entry is committed in the same transaction
    7. If flagged = true, response includes a "pending_review" notice

## Request flow example: computing risk score

    1. Client requests /trees/{id}/risk
    2. Risk Engine Service pulls monitoring_records for that tree
    3. Computes w1-w4 per 06-risk-engine.md
    4. Returns score, bucket, and breakdown (not just a number -
       the explanation is part of the response, for transparency)

## API surface (initial)

    POST   /auth/login
    GET    /trees
    GET    /trees/{id}
    POST   /trees
    PATCH  /trees/{id}
    POST   /trees/{id}/monitoring
    GET    /trees/{id}/monitoring
    GET    /trees/{id}/risk
    GET    /trees/{id}/audit
    GET    /reports/summary

## Why this shape

Audit logging happens at the service layer, not the database layer,
so every write path (not just direct SQL) is guaranteed to produce
a log entry - this matters for the "tamper-evident" claim in
07-audit-trail.md.

## Deployment (planned, not yet implemented)

    - Backend: Docker container, FastAPI + Uvicorn
    - Database: PostgreSQL (managed, e.g. Render/Railway for prototype)
    - Frontend: static build, served separately
