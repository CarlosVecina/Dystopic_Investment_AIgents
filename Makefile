include makefiles/*.mk

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Available targets:"
	@echo "Infrastructure:"
	@echo "  data-lake-terraform-apply    - Apply data lake terraform configuration"
	@echo "  data-lake-terraform-destroy  - Destroy data lake terraform resources"
	@echo "  mage-terraform-apply         - Apply mage terraform configuration"
	@echo "  mage-terraform-destroy       - Destroy mage terraform resources"
	@echo ""
	@echo "Environment:"
	@echo "  install-agents              - Install poetry environment without scrape"
	@echo "  install-data-ingestion      - Install poetry environment without agents"
	@echo "  install                     - Full installation with Python 3.11"
	@echo "  generate-requirements       - Generate requirements.txt from poetry"
	@echo ""
	@echo "Application:"
	@echo "  start-project               - Build and start docker containers"
	@echo "  run-app                     - Run streamlit application"
	@echo "  run-fund                    - Run fund agent"
	@echo ""
	@echo "Data Collection:"
	@echo "  run-crunchbase-scraper      - Run Crunchbase data scraper"
	@echo "  start-websocket-kafka-producer - Start financial news websocket producer"
