variable "credentials" {
  default = "./keys/my_creds.json"
}

variable "location" {
  default = "US"
}

variable "bq_dataset_name" {
  description = "BigQuery dataset name"
  default     = "demo_dataset"
}

variable "gcs_storage_class" {
  description = "Bucket Storage class"
  default     = "STANDARD"
}

variable "gsc_bucket_name" {
  description = "Storage bucket name"
  default     = "terraform-demo-20240115-demo-bucket"
}