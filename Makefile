.PHONY: build shell dbshell migrate import-telemetry import-glean up

build:
	docker-compose build

shell:
	docker-compose run --rm server /bin/bash

dbshell:
	docker-compose run --rm -e PGPASSWORD=pass server psql -h db -U postgres

migrate:
	docker-compose run --rm server python manage.py migrate probes

import-telemetry:
	docker-compose run --rm server python manage.py import_telemetry

import-glean:
	docker-compose run --rm server python manage.py import_glean

up:
	docker-compose up
