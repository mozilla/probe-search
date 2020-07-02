from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("probes", "0002_roles")]

    operations = [
        migrations.RunSQL(
            sql=[
                """
                    CREATE TABLE telemetry (
                        id SERIAL PRIMARY KEY,
                        product VARCHAR(100) NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        type VARCHAR(100) NOT NULL,
                        description TEXT NOT NULL,
                        info JSON NOT NULL,
                        search TSVECTOR NOT NULL
                    )
                """,
                "CREATE UNIQUE INDEX telemetry_product_name ON telemetry (product, name)",
                "CREATE INDEX telemetry_search ON telemetry USING GIN (search)",
                "CREATE INDEX telemetry_name_trgm_index ON telemetry USING GIN (name gin_trgm_ops)",
                "GRANT SELECT ON public.telemetry TO web_anon",
            ],
            reverse_sql=[
                "REVOKE SELECT ON public.telemetry FROM web_anon",
                "DROP TABLE telemetry",
            ],
        )
    ]
