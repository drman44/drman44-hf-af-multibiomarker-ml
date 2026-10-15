.PHONY: cohorts validate external revision test

cohorts:
	python scripts/01_build_modeling_cohorts.py

validate:
	python scripts/02_validate_modeling_cohorts.py

external:
	python scripts/04_external_validation.py

revision:
	python scripts/05_revision_analyses.py

test:
	pytest -q
