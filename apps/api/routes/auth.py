"""/login, /login/select-tenant, /signup.

The two-step auth flow designed for this project: /login verifies
email+password and either returns a full JWT directly (single-tenant
user) or a short-lived pre-auth token + tenant list (multi-tenant
user); /login/select-tenant verifies the pre-auth token and issues the
full JWT. Calls into apps/repository.py and apps/utils/security.py;
nothing here yet.
"""
