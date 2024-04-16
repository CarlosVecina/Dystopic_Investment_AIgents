.PHONY: mage-terraform-apply  mage-terraform-destroy start-project generate-mage-requirements

mage-terraform-apply:
	cd src/data_ingestion/mage_terraform/ 
	terraform apply

mage-terraform-destroy:
	cd src/data_ingestion/mage_terraform/ 
	terraform destroy

start-project:
	docker build . -t mage -f Dockerfile
	docker compose up

generate-mage-requirements:
	poetry export -f requirements.txt --output requirements.txt
