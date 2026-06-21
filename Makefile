.PHONY: install run test lint format docker-build

install:
	python -m pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --reload

test:
	pytest --cov=app --cov-report=term-missing

lint:
	ruff check .

format:
	ruff format .

docker-build:
	docker build -t ai-inference-platform:local .

