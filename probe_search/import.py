import datetime

from mozilla_schema_generator.glean_ping import GleanPing
from mozilla_schema_generator.main_ping import MainPing
from peewee import EXCLUDED, chunked, fn
from google.cloud import bigquery

from probe_search.db import Probes, db
from probe_search.utils import snake_case


def log(message):
    print(
        "{stamp} - {message}".format(
            stamp=datetime.datetime.now().strftime("%x %X"), message=message
        ),
        flush=True,
    )


def get_processes_per_probe():
    """
    Returns a dict keyed by metric with the processes this probe has been
    recorded in.

    For Firefox Desktop only.

    """

    bq = bigquery.Client()

    query = """
        SELECT
            metric,
            ARRAY_AGG(DISTINCT(process)) AS processes,
        FROM
            `moz-fx-data-shared-prod.telemetry_derived.client_probe_counts_v1`
        GROUP BY
            metric
    """
    query_config = bigquery.QueryJobConfig()
    job1 = bq.query(query, job_config=query_config)
    result = job1.result()

    processes = {}
    if result.total_rows > 0:
        for row in result:
            processes[row.metric] = row.processes

    print(
        f" - Fetched {len(processes.keys()):,} probe processes from "
        "GLAM's BigQuery table."
    )
    return processes


def import_probes(product, probes):
    data = []
    if product == "desktop":
        processes = get_processes_per_probe()

    for probe in probes:
        name = snake_case(probe.name)
        definition = probe.definition
        if product == "desktop":
            definition["seen_in_processes"] = processes.get(name, [])
        description = definition["description"]

        data.append(
            {
                "product": product,
                "name": name,
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
