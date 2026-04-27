.PHONY: check compile install-hooks lint pre-commit type

PYTHON ?= python3

check: compile lint type

compile:
	$(PYTHON) -m py_compile scripts/run_particle_analysis.py scripts/__init__.py

install-hooks:
	$(PYTHON) -m pre_commit install

lint:
	$(PYTHON) -m ruff check .

pre-commit:
	$(PYTHON) -m pre_commit run --all-files

type:
	$(PYTHON) -m basedpyright
