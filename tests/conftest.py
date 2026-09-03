"""Shared pytest fixtures: test DB engine/session (pointed at a disposable
schema or the dockerized postgres), an async test client for apps/api, and
seed helpers for tenants/users/roles. Nothing here yet — needed before
tests/integration/test_tenant_isolation.py can run against real data.
"""
