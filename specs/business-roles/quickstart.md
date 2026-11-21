# US-BUSINESS-ROLES quickstart

Run the proofs from the repository root.

```bash
uv run pytest tests/test_business_role_skills.py tests/test_business_role_skills_served.py
```

Expected once built: every skill has its five sections, a gate and existing composed skills, and the served run of `order-to-cash` stops at the approval request.
