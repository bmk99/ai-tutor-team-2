# Deprecated: DB access no longer goes through a SQLAlchemy session dependency.
# Routes call service functions directly, which use the supabase-py client
# from app.core.supabase_client.
