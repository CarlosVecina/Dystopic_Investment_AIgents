# Environment Setup
.PHONY: install-agents install-data-ingestion install generate-mage-requirements

install-agents:
	poetry install --with agents

install-data-ingestion:
	poetry install --with data_ingestion

install:
	poetry install --with dev
	poe force-cuda11 

generate-requirements:
	poetry export -f requirements.txt --output requirements.txt
