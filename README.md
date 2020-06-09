# Probe Search API

This project builds and exposes a PostgREST API on top of a Postgresql
database containing the telemetry and Glean probes.

## Setup

To run locally using Docker and Docker compose, first initialize the database:

    make init
    
Then execute the probe import by running:

     make import
     
To launch the API service run:

     make up
     
This launches the Docker containers to start the database and PostgREST
service.

You can execute `curl` commands against the API. For example, to search for
the desktop probes "GC_MS", try this command:

    curl -X GET "http://0.0.0.0:3000/probes?select=name,definition&product=eq.desktop&or=(name.eq.gc_ms,index.fts(english).gc_ms)" -H "accept: application/json"

The Docker Compose file also launches the Swagger UI to interact with the API
in a web UI way. Visit the Swagger UI at: http://localhost:8080/
