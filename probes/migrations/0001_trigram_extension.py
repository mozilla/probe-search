from django.db import migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.RunSQL(
            sql=["CREATE EXTENSION IF NOT EXISTS pg_trgm"],
            reverse_sql=["DROP EXTENSION pg_trgm"],
        )
    ]
