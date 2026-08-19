# Database Design

## Entities

- users
- species
- trees
- monitoring_records
- audit_logs

## Relationships

    trees.species_id      -> species.id
    trees.created_by      -> users.id
    monitoring_records.tree_id -> trees.id
    monitoring_records.checked_by -> users.id
    audit_logs.tree_id    -> trees.id
    audit_logs.user_id    -> users.id

## Schema

### users
- id (PK)
- name
- email (unique)
- password_hash
- role (admin | field_officer | viewer)
- created_at

### species
- id (PK)
- common_name
- scientific_name
- expected_growth_rate_cm_per_month

### trees
- id (PK)
- tree_code (unique, e.g. TP-KEN-2026-000123)
- species_id (FK -> species.id)
- county
- gps_lat
- gps_lng
- planting_date
- verification_status (pending | verified)
- current_health_status (cached snapshot, not source of truth)
- created_by (FK -> users.id)
- created_at

### monitoring_records
- id (PK)
- tree_id (FK -> trees.id)
- checked_by (FK -> users.id)
- check_date
- height_cm
- health_status (healthy | moderate | at_risk)
- photo_url
- notes

### audit_logs
- id (PK)
- tree_id (FK -> trees.id)
- user_id (FK -> users.id)
- field_changed
- old_value
- new_value
- timestamp
- action_type (create | update | verify | flag)
- flagged (boolean)

## Design notes

- current_health_status on `trees` is a denormalized cache for fast
  reads (e.g. map marker color). The Risk Engine and history views
  always read from monitoring_records, the source of truth.
- Sensitive-field changes on `trees` (gps_lat, gps_lng, verification_status,
  species_id) trigger an audit_logs entry with flagged = true, per the
  rules in 07-audit-trail.md.
- Every monitoring_record insert also produces an audit_logs entry with
  action_type = create; flagged = false unless it results in a
  sensitive-field change on the parent tree.
