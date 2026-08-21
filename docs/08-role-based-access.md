# Role-Based Access Control

## Roles
- admin - full access
- field_officer - can create/update trees and monitoring records
- viewer - read-only access

## Permission matrix

| Endpoint | admin | field_officer | viewer |
|---|---|---|---|
| POST /trees | yes | yes | no |
| GET /trees, GET /trees/id | yes | yes | yes |
| PATCH /trees/id | yes | yes | no |
| POST /trees/id/monitoring | yes | yes | no |
| GET /trees/id/monitoring | yes | yes | yes |
| GET /trees/id/risk | yes | yes | yes |
| GET /trees/id/audit | yes | yes | no |
| GET /reports/* | yes | yes | yes |

## Rationale
- Read access (trees, monitoring history, risk scores, public reports)
  is open to all authenticated roles, including viewer - this supports
  the "public/transparent impact reporting" goal from the project brief.
- Write access (create/update trees, add monitoring records) requires
  field_officer or admin - a viewer should never be able to alter
  field data.
- The audit log is restricted to admin and field_officer only, since it
  can reveal user identities and change history not meant for public
  viewers.

## Implementation approach
A reusable `require_role(*roles)` dependency wraps `get_current_user`
and raises 403 if the authenticated user's role is not in the allowed
set. Applied per-endpoint rather than per-router, since permissions
differ between GET and write operations on the same resource.
