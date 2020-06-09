# Call this to initialize the project and create the tables and other
# operations on first run.

from peewee import ProgrammingError

from probe_search.db import db, Probes


db.connect()

try:
    with db.atomic():
        db.execute_sql("CREATE ROLE web_anon NOLOGIN")
except ProgrammingError:
    pass

db.create_tables([Probes])

db.execute_sql("GRANT USAGE ON SCHEMA public TO web_anon")
db.execute_sql("GRANT SELECT ON public.probes TO web_anon")

# Activate the `pg_trgm` extension.
db.execute_sql("CREATE EXTENSION pg_trgm")

# Create a trigram index on the probes.name column
# This is not supported in peewee so we are doing it here.
db.execute_sql(
    "CREATE INDEX probes_name_trgm_idx "
    "ON probes "
    "USING GIN(name gin_trgm_ops)"
)
