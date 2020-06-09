.PHONY: build shell dbshell import up

build:
	docker-compose build

shell:
	docker-compose run --rm server /bin/bash

dbshell:
	docker-compose run -e PGPASSWORD=pass server psql -h db -U postgres

init:
	docker-compose run --rm server python -m probe_search.initialize

import:
	docker-compose run --rm server python -m probe_search.import

up:
	docker-compose up
