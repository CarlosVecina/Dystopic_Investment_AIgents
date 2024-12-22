# Application Running
.PHONY: start-project run-app run-fund

start-project:
	docker build . -t mage -f Dockerfile
	docker compose up

run-app:
	poetry run streamlit run portfolio_app/app.py

run-fund:
	poetry run python -m dystopic_investment_aigents.agents.fund