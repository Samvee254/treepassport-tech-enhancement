from datetime import datetime, timezone
from app import models

HEALTH_ORDER = {"healthy": 0, "moderate": 1, "at_risk": 2}


def compute_risk(tree: models.Tree, records: list[models.MonitoringRecord]) -> dict:
    breakdown = {}

    if not records:
        return {
            "score": 100,
            "bucket": "HIGH",
            "label": "At Risk",
            "breakdown": {"no_monitoring_data": 100},
            "recommendation": "No monitoring history found. Field inspection required.",
        }

    latest = records[-1]
    previous = records[-2] if len(records) > 1 else None

    # w1: days since last check-in
    days_since = (datetime.now(timezone.utc) - latest.check_date.replace(tzinfo=timezone.utc)).days
    if days_since <= 13:
        w1 = 0
    elif days_since <= 30:
        w1 = 10
    elif days_since <= 45:
        w1 = 25
    else:
        w1 = 40
    breakdown["days_since_last_checkin"] = {"value": days_since, "points": w1}

    # w2: growth trend vs expected rate
    w2 = 0
    if previous and tree.species and tree.species.expected_growth_rate_cm_per_month:
        months_elapsed = max(
            (latest.check_date - previous.check_date).days / 30.0, 0.01
        )
        expected_growth = tree.species.expected_growth_rate_cm_per_month * months_elapsed
        actual_growth = (latest.height_cm or 0) - (previous.height_cm or 0)
        if expected_growth > 0:
            ratio = actual_growth / expected_growth
            if ratio >= 1.0:
                w2 = 0
            elif ratio >= 0.8:
                w2 = 15
            else:
                w2 = 30
    breakdown["growth_trend"] = {"points": w2}

    # w3: health status
    health_points = {"healthy": 0, "moderate": 20, "at_risk": 35}
    w3 = health_points.get(latest.health_status, 0)
    declined = (
        previous is not None
        and HEALTH_ORDER.get(latest.health_status, 0)
        > HEALTH_ORDER.get(previous.health_status, 0)
    )
    if declined:
        w3 += 10
    breakdown["health_status"] = {
        "current": latest.health_status,
        "declined_since_previous": declined,
        "points": w3,
    }

    # w4: missing check-ins (simple placeholder: not enough data to compute
    # a real cadence yet, so 0 until we define expected check-in frequency)
    w4 = 0
    breakdown["missing_checkins"] = {"points": w4}

    score = min(w1 + w2 + w3 + w4, 100)

    if score <= 20:
        bucket, label = "LOW", "Healthy"
    elif score <= 55:
        bucket, label = "MEDIUM", "Watch"
    else:
        bucket, label = "HIGH", "At Risk"

    # Decline override: an active health decline should never be masked
    # by a low raw score (see 06-risk-engine.md revision notes)
    if declined and bucket == "LOW":
        bucket, label = "MEDIUM", "Watch"

    recommendation = (
        "Field inspection required." if bucket == "HIGH"
        else "Monitor closely at next scheduled check-in." if bucket == "MEDIUM"
        else "No action needed."
    )

    return {
        "score": score,
        "bucket": bucket,
        "label": label,
        "breakdown": breakdown,
        "recommendation": recommendation,
    }
