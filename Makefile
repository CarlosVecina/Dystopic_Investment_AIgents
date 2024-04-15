.PHONY: mage-terraform-apply  mage-terraform-destroy start-mage export-requirements

mage-terraform-apply:
	cd src/data_ingestion/mage_terraform/ 
	terraform apply

mage-terraform-destroy:
	cd src/data_ingestion/mage_terraform/ 
	terraform destroy

start-mage:
	docker build . -f Dockerfile --no-cache
	docker compose up

generate-requirements:
	poetry export -f requirements.txt --output requirements.txt
