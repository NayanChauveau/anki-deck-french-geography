.PHONY: check validate schema maps preview build push test format
check validate schema maps preview build push:
	uv run --frozen french-geography $@
test:
	uv run --frozen pytest
format:
	uv run --frozen ruff check --fix .
	uv run --frozen ruff format .
