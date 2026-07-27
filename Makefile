.DEFAULT_GOAL := help
PY := ./.venv/bin

help:           ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install:        ## Install the package
	$(PY)/pip install -e .

dev:            ## Install with dev tooling and git hooks
	python3 -m venv .venv
	$(PY)/pip install -e ".[dev]"
	$(PY)/pre-commit install

test:           ## Run the test suite
	$(PY)/pytest

lint:           ## Lint and check formatting
	$(PY)/ruff check .
	$(PY)/black --check .

format:         ## Auto-fix lint issues and format
	$(PY)/ruff check --fix .
	$(PY)/black .

audit:          ## Run playbook-doctor against this repo (dogfood)
	$(PY)/playbook-doctor check .

clean:          ## Remove caches and build artifacts
	rm -rf .pytest_cache .ruff_cache build dist *.egg-info
	find . -name __pycache__ -not -path "./.venv/*" -exec rm -rf {} +

.PHONY: help install dev test lint format audit clean
