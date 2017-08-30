#!/usr/bin/python3
__author__ = 'rafael'
__version__ = '0.0'


# Compute and network
from azure.common.credentials import ServicePrincipalCredentials
from msrestazure.azure_cloud import AZURE_US_GOV_CLOUD


from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient

from msrestazure import azure_exceptions

# Cloud definitions:
# AZURE_PUBLIC_CLOUD
# AZURE_CHINA_CLOUD
# AZURE_US_GOV_CLOUD
# AZURE_GERMAN_CLOUD

# Resource Group
GROUP_NAME = 'Test_RG'

# Network
VNET_NAME = 'Test_VNet'
SUBNET_NAME = 'Test_subnet'


# Tenant ID for Azure Subscription
TENANT_ID = ''

# Service Principal App ID
CLIENT = ''

# Service Principal Password
KEY = ''

credentials = ServicePrincipalCredentials(
    client_id=CLIENT,
    secret=KEY,
    tenant=TENANT_ID,
    cloud_environment=AZURE_US_GOV_CLOUD)

# Subscription ID
subscription_id = ''

# Client example
compute_client = ComputeManagementClient(credentials, subscription_id,
                                         base_url=AZURE_US_GOV_CLOUD.endpoints.resource_manager)

# Client example
network_client = NetworkManagementClient(credentials, subscription_id,
                                         base_url=AZURE_US_GOV_CLOUD.endpoints.resource_manager)

# List VMs
for vm in compute_client.virtual_machines.list_all():
    print("\tVM: {}".format(vm.name))

# Create Subnet
try:
    async_subnet_creation = network_client.subnets.create_or_update(
        GROUP_NAME,
        VNET_NAME,
        SUBNET_NAME,
        {'address_prefix': '10.70.76.0/24'}
    )

except azure_exceptions.CloudError as e:
    print(e.response.content)

subnet_info = async_subnet_creation.result()

print(subnet_info)

###############################################################################
# Create a resource group and list all resource groups
from azure.mgmt.resource import ResourceManagementClient

# Create client
client = ResourceManagementClient(credentials, subscription_id)

# Create resource group
RESOURCE_GROUP_NAME = 'My_resource_group'


client.resource_groups.create(RESOURCE_GROUP_NAME, {'location':'eastus'})

# Lists resource groups
resource_groups = client.resource_groups.list()
for group in resource_groups:
    print(group.name)

###############################################################################
# Create deployment from template

from azure.mgmt.resource.resources.models import Deployment
from azure.mgmt.resource.resources.models import DeploymentProperties
from azure.mgmt.resource.resources.models import DeploymentMode
from azure.mgmt.resource import ResourceManagementClient

deployment_name = 'MyDeployment'

template = {
  "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "location": {
      "type": "string",
      "allowedValues": [
        "East US",
        "West US",
        "West Europe",
        "East Asia",
        "South East Asia"
      ],
      "metadata": {
        "description": "Location to deploy to"
      }
    }
  },
  "resources": [
    {
      "type": "Microsoft.Compute/availabilitySets",
      "name": "availabilitySet1",
      "apiVersion": "2015-05-01-preview",
      "location": "[parameters('location')]",
      "properties": {}
    }
  ]
}

# Note: when specifying values for parameters, omit the outer elements $schema, contentVersion, parameters
parameters = {"location": { "value": "West US"}}

# Tenant ID for Azure Subscription
TENANT_ID = ''

# Service Principal App ID
CLIENT = ''

# Service Principal Password
KEY = ''

credentials = ServicePrincipalCredentials(
    client_id=CLIENT,
    secret=KEY,
    tenant=TENANT_ID,
    cloud_environment=AZURE_US_GOV_CLOUD)

# Subscription ID
subscription_id = ''

# Resource group
group_name = 'My_RG'

resource_client = ResourceManagementClient(credentials, subscription_id)  # Added by RGM

result = resource_client.deployments.create_or_update(
    group_name,
    deployment_name,
    properties=DeploymentProperties(
        mode=DeploymentMode.incremental,
        template=template,
        parameters=parameters,
    )
)


