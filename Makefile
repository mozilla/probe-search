.PHONY: build shell dbshell

build:
	docker-compose build

shell:
	docker-compose run server /bin/bash

dbshell:
	docker-compose run -e PGPASSWORD=pass server psql -h db -U postgres
