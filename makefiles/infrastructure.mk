# Infrastructure Management
.PHONY: data-lake-terraform-apply data-lake-terraform-destroy mage-terraform-apply mage-terraform-destroy

data-lake-terraform-apply:
	cd dystopic_investment_aigents/data_ingestion/terraform/data_lake_terraform/
	terraform apply

data-lake-terraform-destroy:
	cd dystopic_investment_aigents/data_ingestion/terraform/data_lake_terraform/
	terraform apply

mage-terraform-apply:
	cd dystopic_investment_aigents/data_ingestion/terraform/mage_terraform/
	terraform apply

mage-terraform-destroy:
	cd dystopic_investment_aigents/data_ingestion/terraform/mage_terraform/
	terraform destroy 