import gzip
import json
import urllib.request

from django.core.management.base import BaseCommand
from django.db import connection
from google.cloud import bigquery
from probes.utils import snake_case


PROBES_URL = "https://probeinfo.telemetry.mozilla.org/firefox/all/main/all_probes"


class Command(BaseCommand):

    help = "Adds or updates telemetry probe data from the probe info service."

    def handle(self, *args, **kwargs):

        probes_dict = json.loads(
            gzip.decompress(urllib.request.urlopen(PROBES_URL).read())
        )
        processes = self.get_processes_per_probe()

        data = []
        for v in probes_dict.values():
            name = snake_case(v["name"])
            history = (
                v["history"].get("nightly")
                or v["history"].get("beta")
                or v["history"].get("release")
            )[0]
            description = history["description"].strip()

            # Add a calculated property for info we calculate from the probeinfo data.
            calculated = {
                "active": name in processes,
                "seen_in_processes": processes.get(name, []),
                "latest_history": history,
            }
            v["calculated"] = calculated

            data.append(
                {
                    "product": "firefox",
                    "name": name,
                    "type": v["type"],
                    "description": description,
                    "info": json.dumps(v),
                }
            )

        # Insert or update into tables.
        sql = """
            INSERT INTO telemetry (product, name, type, description, info, search)
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

        print(f"Imported {len(data):,} telemetry probes.")

    def get_processes_per_probe(self):
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
                `moz-fx-data-shared-prod.telemetry.client_probe_counts`
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
