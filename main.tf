provider "google" {
  project = "yonidev"
  region  = "us-central1"
}

terraform {
  backend "gcs" {
    bucket  = "tf_state_scrapy"
    prefix  = "terraform/state"
  }
}

data "external" "generate_zip_file" {
  program = ["python", "create_zip.py"]
}

locals {
  bucket_name           = "ramilevy_scrapy_bucket"
  topic_name            = "ramilevy_scrapy_topic"
}

# Create the topic only if it doesn't exist
resource "google_pubsub_topic" "ramilevy_scrapy_topic" {
  name  = local.topic_name
}

# Step 1: Upload the ZIP file to Google Cloud Storage
resource "google_storage_bucket" "ramilevy_scrapy_bucket" {
  name     = local.bucket_name
  location = "US"
}

resource "google_storage_bucket_object" "function_zip_object" {
  name   = data.external.generate_zip_file.result["zip_file_name"]
  bucket = google_storage_bucket.ramilevy_scrapy_bucket.name
  source = data.external.generate_zip_file.result["zip_file_name"]
}

resource "google_cloudfunctions_function" "ramilevy_scrapy" {
  name    = "ramilevy_scrapy"
  runtime = "python311"
  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.ramilevy_scrapy_topic.name
  }
  source_archive_bucket = google_storage_bucket.ramilevy_scrapy_bucket.name
  source_archive_object = google_storage_bucket_object.function_zip_object.name
  entry_point           = "collect_orders"
  environment_variables = {
    USER1           = var.USER1
    PASSWORD1       = var.PASSWORD1
    REDIS_HOST      = var.REDIS_HOST
    REDIS_PORT      = var.REDIS_PORT
    REDIS_PASSWORD  = var.REDIS_PASSWORD
  }
}


resource "google_cloud_scheduler_job" "ramilevy_scrapy_job" {
  name     = "ramilevy_scrapy-job"
  schedule = "0 0 * * *"
  pubsub_target {
    topic_name = "projects/yonidev/topics/${google_pubsub_topic.ramilevy_scrapy_topic.name}"
    data       = base64encode("Scheduled job message")
  }
}

resource "null_resource" "delete_zip_file" {
  triggers = {
    # Depend on the ZIP file name generated by the Python script
    zip_file_name = data.external.generate_zip_file.result["zip_file_name"]
  }

  provisioner "local-exec" {
    command = "rm -f ${data.external.generate_zip_file.result["zip_file_name"]}"
  }
  depends_on = [google_cloudfunctions_function.ramilevy_scrapy]
}

variable "USER1" {
  description = "User1 variable for your Google Cloud Function"
}

variable "PASSWORD1" {
  description = "Password1 variable for your Google Cloud Function"
}

variable "REDIS_HOST" {
  description = "Redis host for your Google Cloud Function"
}

variable "REDIS_PORT" {
  description = "Redis port for your Google Cloud Function"
}

variable "REDIS_PASSWORD" {
  description = "Redis password for your Google Cloud Function"
}