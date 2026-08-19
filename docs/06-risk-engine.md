# Tree Health Risk Engine — Design

## Purpose
Convert monitoring history into an explainable risk score, flagging trees
that need field attention before they visibly decline.

## Inputs
- Days since last check-in
- Growth rate (actual vs. species-expected)
- Current + previous health status
- Count of missed scheduled check-ins

## Scoring Model

RISK SCORE = w1 + w2 + w3 + w4  (0-100 scale)

w1: Days since last check-in
- 0-13 days   -> 0 pts
- 14-30 days  -> 10 pts
- 31-45 days  -> 25 pts
- 46+ days    -> 40 pts

w2: Growth trend vs. species-expected rate
- At/above expected      -> 0 pts
- Slightly below (<20%)  -> 15 pts
- Significantly below    -> 30 pts

w3: Health status
- Healthy   -> 0 pts
- Moderate  -> 20 pts
- At Risk   -> 35 pts
- +10 pts if status declined since previous check-in

w4: Missing scheduled check-ins
- 0 missed -> 0 pts
- 1 missed -> 10 pts
- 2+ missed -> 15 pts

## Buckets
| Score  | Bucket | Label    |
|--------|--------|----------|
| 0-30   | LOW    | Healthy  |
| 31-60  | MEDIUM | Watch    |
| 61-100 | HIGH   | At Risk  |

## Output example

    TREE AT RISK
    Tree ID: TP-KEN-2026-000123
    Score: 75 (HIGH)
      - Last check-in: 47 days ago (+40)
      - Growth: below expected range (+30)
      - Previous health: Healthy, now Moderate (+20, +10 decline bonus)
    Recommendation: Field inspection required.

## Future extension
Once real check-in data exists at scale, this rule-based model can be
replaced or supplemented with a trained classifier (e.g. scikit-learn
logistic regression or gradient boosting) using the same features plus
environmental data (rainfall, temperature) if available.

## Explicit distinction
This scoring engine is a proposed enhancement. Nothing here claims
TreePassport already performs risk scoring - it is our addition on top
of the existing monitoring data model.
