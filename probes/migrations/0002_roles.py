from django.db import migrations



class Migration(migrations.Migration):

    dependencies = [("probes", "0001_trigram_extension")]

    operations = [
        migrations.RunSQL(
            sql=[
                "CREATE ROLE web_anon NOLOGIN",
                "GRANT USAGE ON SCHEMA public TO web_anon",
            ],
            reverse_sql=[
                "REVOKE USAGE ON SCHEMA public FROM web_anon",
                "DROP ROLE web_anon",
            ],
        )
    ]

