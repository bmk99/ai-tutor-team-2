# Deprecated: tables are no longer auto-created via SQLAlchemy metadata.
# Since the app now talks to Supabase over its REST API (supabase-py client,
# see app/core/supabase_client.py), schema DDL isn't reachable from here.
# Run app/db/schema.sql once in the Supabase SQL editor to create the tables.
