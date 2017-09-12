#!/usr/bin/python3
__author__ = 'rafael'
__version__ = '0.2'

"""Creates resource group if necessary, loads json, and delete json if necessary."""

import datetime
import os.path
import json
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
from msrestazure.azure_cloud import AZURE_US_GOV_CLOUD


class Loader:
    """
    Initialize the Loader class with a Resource Management Client
    with Service Principal credentials
    """

    def __init__(
            self,
            cloud_definition,
            tenant,
            location,
            subscription_id,
            resource_group,
            service_principal,
            secret,
            template_name
    ):
        self.cloud_definition = cloud_definition
        self.tenant = tenant
        self.location = location
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.service_principal = service_principal
        self.secret = secret
        self.template_name = template_name

        self.template = None
        self.base_url = None

        if self.cloud_definition == 'azure_gov':
            self.cloud_definition = AZURE_US_GOV_CLOUD
            self.base_url = AZURE_US_GOV_CLOUD.endpoints.resource_manager

        self.credentials = ServicePrincipalCredentials(
            client_id=self.service_principal,
            secret=self.secret,
            tenant=self.tenant,
            cloud_environment=self.cloud_definition
        )

        self.client = ResourceManagementClient(
            self.credentials,
            self.subscription_id,
            base_url=self.base_url
        )

    def create_resource_group(self):
        """Create resource group"""
        result = self.client.resource_groups.create_or_update(
            self.resource_group,
            {
                'location': self.location
            }
        )
        print('Created resource or update group: {}'.format(result))

    def get_template(self):
        try:
            template_path = os.path.join(os.path.dirname(__file__), "Templates", self.template_name)
            with open(template_path, 'r') as template_file_fd:
                template = json.load(template_file_fd)
        except IOError:
            print("An IOError has occurred!" + template_path)
        self.template = template
        return self.template

    def deploy(self):
        """Deploy template"""

        self.create_resource_group()

        deployment_properties = {
            'mode': DeploymentMode.incremental,
            'template': self.get_template()
        }

        # deployment_async_operation = self.client.deployment_operations.create_or_update()
        # self.client.deployments.create_or_update()

        deployment_async_operation = self.client.deployments.create_or_update(
            self.resource_group,
            '{}_{}'.format(self.resource_group, datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')),
            deployment_properties
        )

        deployment_async_operation.wait()

        # def destroy(self):
        #     """Destroy the given resource group"""
        #     self.client.resource_groups.delete(self.resource_group)


def main():
    cloud_definition = ''
    tenant = ''
    location = ''
    subscription_id = ''
    resource_group = ''
    chq_dr_test_sp = ''
    secret = ''

    template_name = ''

    loader_object = Loader(cloud_definition, tenant, location, subscription_id,
                           resource_group, chq_dr_test_sp, secret, template_name)

    loader_object.deploy()


if __name__ == '__main__':
    main()