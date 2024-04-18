# main.tf

terraform {
  required_version = ">= 0.14"

  required_providers {
    # Cloud Run support was added on 3.3.0
    google = ">= 3.3"
  }
}

provider "google" {
  project     = var.project_id
  region      = var.region
  zone        = var.zone
  credentials = file("./keys/my_creds.json")
}

resource "google_compute_instance" "default" {
  name         = "my-instance"
  machine_type = "n2-standard-2" # $0.12703 hourly
  zone         = var.zone

  tags = ["foo", "bar"]

  boot_disk {
    initialize_params {
      image = var.ubuntu_2004_sku
      labels = {
        my_label = "value"
      }
    }
  }

  // Local SSD disk
  scratch_disk {
    interface = "NVME"
  }

  network_interface {
    network = "default"

    access_config {
      // Ephemeral public IP
    }
  }

  metadata = {
    foo = "bar"
  }

  metadata_startup_script = "echo hi > /test.txt"

}