dev:		## Run both services locally
	docker compose up --build

lint:		## Lint & type-check
	tox -e lint,type

test:		## Run pytest
	tox -e py
