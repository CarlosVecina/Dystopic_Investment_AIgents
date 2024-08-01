.PHONY: data-lake-terraform-apply data-lake-terraform-destroy mage-terraform-apply  mage-terraform-destroy start-project install-env generate-mage-requirements run-crunchbase-scraper

data-lake-terraform-apply:
	cd src/data_ingestion/terraform/data_lake_terraform/ 
	terraform apply

data-lake-terraform-destroy:
	cd src/data_ingestion/terraform/data_lake_terraform/ 
	terraform apply

generate-mage-requirements:
	poetry export -f requirements.txt --output requirements.txt

install-env:
	poetry install --without scrape

mage-terraform-apply:
	cd src/data_ingestion/terraform/mage_terraform/ 
	terraform apply

mage-terraform-destroy:
	cd src/data_ingestion/terraform/mage_terraform/ 
	terraform destroy

run-crunchbase-scraper:
	poetry run python src/data_ingestion/download_crunchbase_data.py --is_local=True

start-project:
	docker build . -t mage -f Dockerfile
	docker compose up

start-websocket-kafka-producer:
	poetry run python3 src/data_ingestion/download_financial_news.py --url wss://paper-api.alpaca.markets/stream

run-app:
	poetry run streamlit run src/app/app.py   