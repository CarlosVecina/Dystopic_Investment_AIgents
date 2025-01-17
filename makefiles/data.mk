# Data Collection
.PHONY: run-crunchbase-scraper start-websocket-kafka-producer

run-crunchbase-scraper:
	poetry run python dystopic_investment_aigents/data_ingestion/download_crunchbase_data.py --is_local=True

start-websocket-kafka-producer:
	poetry run python3 dystopic_investment_aigents/data_ingestion/download_financial_news.py --url wss://paper-api.alpaca.markets/stream
