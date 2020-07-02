from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("probes", "0003_telemetry")]

    operations = [
        migrations.RunSQL(
            sql=[
                """
                    CREATE TABLE glean (
                        id SERIAL PRIMARY KEY,
                        product VARCHAR(100) NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        type VARCHAR(100) NOT NULL,
                        description TEXT NOT NULL,
                        info JSON NOT NULL,
                        search TSVECTOR NOT NULL
                    )
                """,
                "CREATE UNIQUE INDEX glean_product_name ON glean (product, name)",
                "CREATE INDEX glean_search ON glean USING GIN (search)",
                "CREATE INDEX glean_name_trgm_index ON glean USING GIN (name gin_trgm_ops)",
                "GRANT SELECT ON public.glean TO web_anon",
            ],
            reverse_sql=[
                "REVOKE SELECT ON public.glean FROM web_anon",
                "DROP TABLE glean",
            ],
        )
    ]
