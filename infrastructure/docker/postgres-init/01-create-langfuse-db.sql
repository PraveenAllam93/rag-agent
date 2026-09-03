-- Runs once, only on a brand-new (empty) postgres data directory.
-- Gives Langfuse its own database in the shared postgres instance so its
-- migrations never collide with the application schema.
--
-- If postgres was already initialized before this file existed, it will
-- NOT run automatically. Create the database by hand instead:
--   docker exec -it postgres psql -U postgres -c "CREATE DATABASE langfuse;"
CREATE DATABASE langfuse;
