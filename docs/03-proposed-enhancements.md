# Proposed Enhancements

## Candidate list (ranked)

| # | Enhancement | Impact | Difficulty | Uniqueness | Demo value |
|---|---|---|---|---|---|
| 1 | Tree Health Risk Engine | High | Medium | High | Very high |
| 2 | Audit Trail / tamper-evident change log | High | Low-Medium | High | High |
| 3 | Interactive GIS map with filtering | Medium | Low | Medium | High |
| 4 | Automated impact report generator (PDF/CSV) | Medium | Low | Low | Medium |
| 5 | Role-based access control (Admin/Field Officer/Viewer) | Medium | Medium | Medium | Medium |

## Selected MVP scope

Signature features (the two hardest, most differentiating problems):
    1. Tree Health Risk Engine   - see 06-risk-engine.md
    2. Audit Trail                - see 07-audit-trail.md

Supporting scaffolding (needed to demonstrate the above, not the focus):
    - Tree record CRUD (trees table, basic API)
    - Monitoring record capture (feeds the Risk Engine)
    - Minimal auth (needed for Audit Trail to have a user_id)

Deferred (not in MVP, noted as future work):
    - GIS map with filtering
    - Automated PDF/CSV report generation
    - Full role-based access control (MVP may use a single role or
      a minimal two-role check, expanded later)

## Rationale
#1 and #2 are the two features that can't be dismissed as "just a
CRUD app with a map" - they directly demonstrate applied AI/data
reasoning and information security thinking, matching the academic
background this project is meant to showcase. #3-#5 are valuable
but conventional; they support the demo rather than define it.

## Explicit distinction
All five items above are proposed enhancements, not existing
TreePassport features. See 02-existing-workflow.md for what is
understood to already exist on the TreePassport platform.
