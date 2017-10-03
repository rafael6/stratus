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

# Credentials set
CLIENT = ''  # SP
KEY = ''  # SP password
TENANT_ID = ''

# Client set
subscription_id = ''

GROUP_NAME = ''
VNET_NAME = ''
SUBNET_NAME = ''

credentials = ServicePrincipalCredentials(
    client_id=CLIENT,
    secret=KEY,
    tenant=TENANT_ID,
    cloud_environment=AZURE_US_GOV_CLOUD)

# Client example
network_client = NetworkManagementClient(credentials, subscription_id,
                                 base_url=AZURE_US_GOV_CLOUD.endpoints.resource_manager)

'''
Create create_update, delete, and get functions for each networknclass at
https://azure-sdk-for-python.readthedocs.io/en/latest/ref/azure.mgmt.network.v2017_03_01.operations.html
'''

# Virtual Networks Functions:
def create_update_vnet(
        resource_group_name,
        virtual_network_name,
        parameters,
        custom_headers=None,
        raw=False):
    """
    Creates or updates a virtual network in the specified resource group.

    :param resource_group_name: (str) – The name of the resource group.
    :param virtual_network_name:
    :param parameters:
    :param custom_headers:
    :param raw:
    :return:
    """

    try:
        async_vnet_creation = network_client.virtual_networks.create_or_update(
            resource_group_name,
            virtual_network_name,
            parameters,
            custom_headers=None,
            raw=False)
        async_vnet_creation.wait()  # !!!
        vnet_info = async_vnet_creation.result()  # !!!
        return vnet_info.result().provisioning_state  # !!!
    except azure_exceptions.CloudError as e:
        return e

network_client.subnets.create_or_update('rg', 'vn', 'su', {})
def main():

    create_update_vnet(
        'my_rg',
        'my_vnet',
        {'location': 'my_location',
         'address_space': {'address_prefixes': ['10.0.0.0/16']},
         'dhcp_options': {'dns_servers': ['8.8.8.8', '8.8.8.8']}}
    )

if __name__ == '__main__':
    main()



