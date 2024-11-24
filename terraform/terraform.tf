# Specify the Terraform version and required providers
terraform {
  required_version = ">= 1.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

# Configure the azurerm provider
provider "azurerm" {
  features {}
}

# Retrieve client configuration
data "azurerm_client_config" "current" {}

# Create Resource Group
# resource "azurerm_resource_group" "aml_rg" {
#   name     = "aml-resources"               
#   location = "East US"                    
# }

# Reference existing Resource Group (aml-resources)
data "azurerm_resource_group" "aml_rg" {
  name = "aml-resources"
}

# Create Azure Data Lake (Storage Account with hierarchical namespace enabled)
# resource "azurerm_storage_account" "aml_storage_account" {
#   name                     = "amldatalakestore"                  
#   resource_group_name      = azurerm_resource_group.aml_rg.name    
#   location                 = azurerm_resource_group.aml_rg.location 
#   account_tier             = "Standard"                           
#   account_replication_type = "LRS"                                
#   is_hns_enabled           = true                                  
# }

# Create Storage Container (folder-like structure in Data Lake)
# resource "azurerm_storage_container" "aml_container" {
#   name                  = "default-prediction-data"                
#   storage_account_name  = azurerm_storage_account.aml_storage_account.name
#   container_access_type = "private"                              
# }

# Reference existing Storage Account
data "azurerm_storage_account" "aml_storage_account" {
  name                = "amldatalakestore"
  resource_group_name = data.azurerm_resource_group.aml_rg.name
}

# Create Key Vault
resource "azurerm_key_vault" "aml_key_vault" {
  name                = "amlkeyvault12345"  # Ensure this is unique
  resource_group_name = data.azurerm_resource_group.aml_rg.name
  location            = data.azurerm_resource_group.aml_rg.location
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"  # Add this line to specify the SKU

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id
    secret_permissions = ["Get", "List", "Set", "Delete"]
  }
}

# Create Application Insights
resource "azurerm_application_insights" "aml_app_insights" {
  name                = "amlappinsights"
  location            = data.azurerm_resource_group.aml_rg.location
  resource_group_name = data.azurerm_resource_group.aml_rg.name
  application_type    = "web"
}

# Create a new storage account for Azure ML without HNS enabled
resource "azurerm_storage_account" "aml_storage_account_no_hns" {
  name                     = "amlstorageaccountnohn"  # Ensure a unique name
  resource_group_name      = data.azurerm_resource_group.aml_rg.name
  location                 = data.azurerm_resource_group.aml_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = false  # Set HNS to false to ensure compatibility
}

data "azurerm_storage_account" "aml_storage_account_no_hns" {
  name                = "amlstorageaccountnohn"
  resource_group_name = data.azurerm_resource_group.aml_rg.name
}

# Create Azure Machine Learning Workspace
resource "azurerm_machine_learning_workspace" "aml_workspace" {
  name                = "aml-machine-learning"
  resource_group_name = data.azurerm_resource_group.aml_rg.name
  location            = data.azurerm_resource_group.aml_rg.location

  sku_name            = "Basic"
  storage_account_id  = azurerm_storage_account.aml_storage_account_no_hns.id
  key_vault_id        = azurerm_key_vault.aml_key_vault.id
  application_insights_id = azurerm_application_insights.aml_app_insights.id

  identity {
    type = "SystemAssigned"
  }

  public_network_access_enabled = true
}

# Create Azure Machine Learning Compute Instance
resource "azurerm_machine_learning_compute_instance" "aml_compute_instance" {
  name                           = "aml-compute-instance-new"
  machine_learning_workspace_id  = azurerm_machine_learning_workspace.aml_workspace.id

  virtual_machine_size           = "Standard_E4ds_v4"

  identity {
    type = "SystemAssigned"  # Assign a system-assigned managed identity
  }
}