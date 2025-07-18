PORT ?= 8000

install:
	uv sync

dev:
	uv run flask --debug --app page_analyzer:app run

start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer.app:app

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer.app:app

build:
	./build.sh

lint:
	uv run ruff check page_analyzer

flake8:
	uv run flake8 page_analyzer
