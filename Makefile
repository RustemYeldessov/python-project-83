install:
	uv sync

dev:
	uv run flask --debug --app page_analyzer:app run

