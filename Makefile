.PHONY: docs

.install-uv:
	uv sync --all-groups --all-extras && source .venv/bin/activate

docs: .install-uv
	uv run mkdocs build

docs-dev: .install-uv
	uv run mkdocs serve --watch .

api: .install-uv
	uv run uvicorn src.gptarot.index:app --reload --reload-dir src

ui: .install-uv
	uv run streamlit run src/gptarot/inference.py
