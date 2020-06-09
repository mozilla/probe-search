import datetime

from mozilla_schema_generator.glean_ping import GleanPing
from mozilla_schema_generator.main_ping import MainPing
from peewee import EXCLUDED, chunked, fn

from probe_search.db import Probes, db
from probe_search.utils import snake_case


def log(message):
    print(
        "{stamp} - {message}".format(
            stamp=datetime.datetime.now().strftime("%x %X"), message=message
        ),
        flush=True,
    )


def import_probes(product, probes):
    data = []
    for probe in probes:
        definition = probe.definition
        description = definition["description"]

        data.append(
            {
                "product": product,
                "name": snake_case(probe.name),
                "type": probe.type,
                "description": description,
                "definition": definition,
                "index": fn.to_tsvector("english", " ".join([probe.name, description])),
            }
        )

    with db.atomic():
        for batch in chunked(data, 100):
            (
                Probes.insert_many(batch)
                .on_conflict(
                    conflict_target=[Probes.product, Probes.name],
                    update={
                        Probes.description: EXCLUDED.description,
                        Probes.definition: EXCLUDED.definition,
                        Probes.index: EXCLUDED.index,
                    },
                )
                .execute()
            )
    log("Imported {n:,} probes for {product}".format(n=len(probes), product=product))


if __name__ == "__main__":
    log("Starting imports...")
    # Import telemetry pings
    import_probes("desktop", MainPing().get_probes())

    # Import Glean pings
    glean_products = [repo[0] for repo in GleanPing.get_repos()]
    for product in glean_products:
        import_probes(product, GleanPing(product).get_probes())
