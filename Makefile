.PHONY: docs

.install-uv:
	@find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete
	@uv sync --all-groups --all-extras && source .venv/bin/activate

docs: .install-uv
	@uv run mkdocs build

docs-dev: .install-uv
	@uv run mkdocs serve --watch .

api: .install-uv
	@uv run uvicorn api.index:app --reload --reload-dir api

ui: .install-uv
	@uv run streamlit run api/inference.py
