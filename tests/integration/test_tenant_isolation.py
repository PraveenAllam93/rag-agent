"""The Phase 1 exit criterion (docs/ROADMAP.md): seed two tenants with a
near-identical document/user each, authenticate as a user in tenant A, and
verify tenant B's rows are unreachable — not just absent from a query
result, but unreachable via any query path, error message, or timing
signal. Written in Phase 1, never removed per CLAUDE.md.

Nothing here yet. Write this failing, before the RLS policies it's meant
to pin down — see .claude/rules/security-invariants.md invariant #1
(tenant filter applied inside the search, never after it).
"""
