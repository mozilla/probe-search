from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("probes", "0004_glean")]

    operations = [
        migrations.RunSQL(
            sql=[
                """
                CREATE VIEW products AS
                    SELECT DISTINCT product FROM telemetry
                    UNION
                    SELECT DISTINCT product FROM glean
                """,
                "GRANT SELECT ON public.products TO web_anon",
            ],
            reverse_sql=[
                "REVOKE SELECT ON public.products FROM web_anon",
                "DROP VIEW products",
            ],
        )
    ]
