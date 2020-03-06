.PHONY: build shell dbshell import up

build:
	docker-compose build

shell:
	docker-compose run server /bin/bash

dbshell:
	docker-compose run -e PGPASSWORD=pass server psql -h db -U postgres

import:
	docker-compose run server python -m probe_search.import

up:
	docker-compose up
