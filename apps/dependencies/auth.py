"""FastAPI Depends() function(s) that decode and verify the JWT from
the Authorization header and return the caller's {user_id, tenant_id,
role_id}. This is how routes learn who's calling — tenant_id/user_id
should never be passed around as plain function arguments elsewhere
in the app once this exists.

Nothing here yet.
"""
