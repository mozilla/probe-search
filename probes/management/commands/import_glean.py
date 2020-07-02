import json

from django.core.management.base import BaseCommand
from django.db import connection
from mozilla_schema_generator.glean_ping import GleanPing
from probes.utils import snake_case


# The schema generator uses sets for some data structures. This will convert
# them to a list when we serialize to JSON when storing the probe
# representation to the database.
class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class Command(BaseCommand):

    help = "Adds or updates glean probe data from mozilla-schema-generator."

    def handle(self, *args, **kwargs):

        glean_products = [repo[0] for repo in GleanPing.get_repos()]
        for product in glean_products:
            probes = GleanPing(product).get_probes()

            data = []
            for probe in probes:
                name = snake_case(probe.name)
                info = probe.definition
                description = info.get("description").strip()

                data.append(
                    {
                        "product": product,
                        "name": name,
                        "type": probe.type,
                        "description": description,
                        "info": json.dumps(info, cls=SetEncoder),
                    }
                )

            self.upsert_data(data)

    def upsert_data(self, data):

        # Insert or update into tables.
        sql = """
            INSERT INTO glean (product, name, type, description, info, search)
            VALUES (
                %s, %s, %s, %s, %s,
                SETWEIGHT(TO_TSVECTOR('simple', %s), 'A') ||
                SETWEIGHT(TO_TSVECTOR('english', %s), 'B')
            )
            ON CONFLICT (product, name)
            DO UPDATE SET
                type = EXCLUDED.type,
                description = EXCLUDED.description,
                info = EXCLUDED.info,
                search = EXCLUDED.search
        """
        for d in data:
            with connection.cursor() as cursor:
                cursor.execute(
                    sql,
                    [
                        d["product"],
                        d["name"],
                        d["type"],
                        d["description"],
                        d["info"],
                        d["name"],
                        d["description"],
                    ],
                )

        print("Imported {:,} glean probes for {}.".format(len(data), d["product"]))
