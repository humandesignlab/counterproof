"""Confidence scoring and escalation stage.

Combines per-field confidence, grounding quality, and check results into an
overall confidence and per-finding severity, then applies an explicit, versioned
escalation policy. The policy is data, not hardcoded. This recommends an action
for a human reviewer; it never makes the underwriting decision.

Skeleton only in Task 1. No scoring logic yet.
"""
