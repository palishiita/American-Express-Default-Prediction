# Specify the Terraform version and required providers
terraform {
  required_version = ">= 1.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.0"
    }
  }
}

# Specify the provider
provider "azurerm" {
  features {}
}

# Configure the Databricks provider
provider "databricks" {
  azure_workspace_resource_id = azurerm_databricks_workspace.databricks_workspace.id
  use_azure_cli               = true
}

# Create Resource Group
resource "azurerm_resource_group" "aml_rg" {
  name     = "aml-resources"
  location = "East US"
}

# Create Azure Data Lake (Storage Account with hierarchical namespace enabled)
resource "azurerm_storage_account" "aml_storage_account" {
  name                     = "amldatalakestore"
  resource_group_name      = azurerm_resource_group.aml_rg.name
  location                 = azurerm_resource_group.aml_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true
}

# Create Storage Container (folder-like structure in Data Lake)
resource "azurerm_storage_container" "aml_container" {
  name                  = "default-prediction-data"
  storage_account_name  = azurerm_storage_account.aml_storage_account.name
  container_access_type = "private"
}

# Create Azure Databricks Workspace
resource "azurerm_databricks_workspace" "databricks_workspace" {
  name                = "aml-databricks-workspace"
  resource_group_name = azurerm_resource_group.aml_rg.name
  location            = azurerm_resource_group.aml_rg.location
  sku                 = "standard" # Can also use "premium" for advanced features
}