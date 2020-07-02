# Probe Search API

This project builds and exposes a PostgREST API on top of a Postgresql
database containing the telemetry and Glean probes.

## Setup

To run locally using Docker and Docker compose, first build the Docker container:

    make build

Next, prepare the database by running the migrations:

    make migrate

Then execute the import script(s) by running either of the following, or both:

     make import-telemetry
     make import-glean
     
To launch the API service run:

     make up
     
This launches the Docker containers to start the database and PostgREST
service.

You can execute `curl` commands against the API. For example, to search for
the desktop probes "GC_MS", try this command:

    curl -X GET "http://0.0.0.0:3000/telemetry?select=name,description&product=eq.firefox&search=plfts(simple).gc_ms" -H "accept: application/json"

The Docker Compose file also launches the Swagger UI to interact with the API
in a web UI way. Visit the Swagger UI at: http://localhost:8080/
