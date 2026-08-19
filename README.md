# TreePassport Technology Enhancement - Prototype

An independent proof-of-concept exploring how technology can enhance
the existing TreePassport workflow (Geo-Tag to Track to Monitor to Report),
built as a demonstration project.

This is not an attempt to rebuild or clone TreePassport.
It is a technology enhancement prototype focused on two signature features:

- Tree Health Risk Engine - rule-based risk scoring from monitoring history
- Audit Trail - tamper-evident logging of record changes

## Status

MVP working end-to-end. Both signature features are implemented,
tested, and running.

### Built so far
- POST /trees, GET /trees, GET /trees/{id} - tree record CRUD
- POST /trees/{id}/monitoring, GET /trees/{id}/monitoring - check-in history
- GET /trees/{id}/risk - Tree Health Risk Engine (scoring + explainable breakdown)
- PATCH /trees/{id} - tree updates with automatic audit logging
- GET /trees/{id}/audit - audit trail for a tree, sensitive-field changes flagged

### Not yet built
- Authentication (currently accepts a raw user_id query param as a placeholder)
- Role-based access control
- GIS map / frontend
- PDF/CSV report generation
- Audit logging on monitoring-record creation (currently only on tree PATCH)

## Design docs

See docs/ for the full design process:
- 01-problem-definition.md and 02-existing-workflow.md - context
- 03-proposed-enhancements.md - ranked candidates and MVP scope
- 04-system-architecture.md - request flow and API surface
- 05-database-design.md - schema
- 06-risk-engine.md - scoring model, including a revision documenting
  a bucket edge case found during testing
- 07-audit-trail.md - audit logging and flagging logic

## Running locally

    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload

Then visit 127.0.0.1:8000/docs for the interactive API.
