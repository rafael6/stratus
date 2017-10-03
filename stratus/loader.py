#!/usr/bin/python3
__author__ = 'rafael'
__version__ = '1.0'

"""
Creates resource group if necessary, deploy json template, and optionally
destroys the resource group and its content.

Usage:
    from stratus import loader

    cloud_definition = 'azure_com'
    tenant = 'my_tenant_id'
    location = 'my_location'
    subscription_id = 'my_subscription_id'
    resource_group = 'my_resource_group'
    service_principal = 'my_service_pricipal'
    sp_key = 'my_service_pricipla_key'
    template_name = "my_json.json"

    load = loader.Loader(cloud_definition, tenant, location, subscription_id,
                               resource_group, service_principal, sp_key, template_name)
    load.deploy()
    print(load)
    load.destroy()
"""

import datetime
import os.path
import json
import sys
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
from msrestazure.azure_cloud import AZURE_US_GOV_CLOUD
from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD
from msrestazure import azure_exceptions
from msrest.exceptions import AuthenticationError


class Loader:
    """
    Initialize the Loader class with a Resource Management Client.

    Args:
        cloud_definition (str): Cloud definition such as azure_gov or azure_com
        tenant (str): The tenant ID.
        location (str): The resource's location
        subscription_id (str): The subscription ID.
        resource_group (str): The resource group.
        service_principal (str): The service principal ID.
        secret (str): The service principal ID.
        template_name (str): The name of the template.
        parameters_values (dic): The parameters; default value is None.

    Attributes:
        template (dict): The JSON document; default is None.
        base_url (str): The base URL object; default is None.
        credentials (ServicePrincipalCredentials): Credential; default is None.
        client (ResourceManagementClient): The Client object; default is None.
        resource_group_output (ResourceGroup): Default is None.
        deployment_output (DeploymentExtended): Default value is None.
        parameters = (dict): parameters as a dictionary; default value is None.
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
            template_name,
            parameters_values=None
    ):
        self.cloud_definition = cloud_definition
        self.tenant = tenant
        self.location = location
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.service_principal = service_principal
        self.secret = secret
        self.template_name = template_name
        self.parameters_values = parameters_values
        self.template = None
        self.base_url = None
        self.credentials = None
        self.client = None
        self.resource_group_output = None
        self.deployment_output = None
        self.parameters = None

        try:
            if self.cloud_definition == 'azure_gov':
                self.cloud_definition = AZURE_US_GOV_CLOUD
            elif self.cloud_definition == 'azure_com':
                self.cloud_definition == AZURE_PUBLIC_CLOUD
            else:
                raise ValueError('Cloud definition must be azure_gov or azure_com.')

            self.base_url = self.cloud_definition.endpoints.resource_manager

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

        except AuthenticationError as e:
            print(e)
            sys.exit(1)
        except ValueError as e:
            print(e)
            sys.exit(1)

    def __str__(self):
        """
        A custom string representation of the object.
        :return: (str)
        """
        try:
            output = '''Deployment details:
        Resource Group Name: {}
        Resource Group ID: {}
        Resource Group Location: {}
        Deployment Name: {}
        Deployment ID: {}
        '''.format(self.resource_group_output.name,
                   self.resource_group_output.id,
                   self.resource_group_output.location,
                   self.deployment_output.name,
                   self.deployment_output.id
                   )
            return output
        except AttributeError as e:
            print('Deployment failed, {}'.format(e))
            sys.exit(1)

    def create_resource_group(self):
        """
        Create resource group for the deployment if the resource group doesn't
        exists.
        :return: (ResourceGroup)
        """
        try:
            result = self.client.resource_groups.create_or_update(
                self.resource_group,
                {
                    'location': self.location
                }
            )
            self.resource_group_output = result
            print('Created or updated resource group {}'.format(self.resource_group_output.name))
        except azure_exceptions.CloudError as e:
            print(e)

    def get_template(self):
        """
        Opens the specified json file from the templates directory and
        serialize it into a dict object.

        :return: (dict), serialized json.
        """
        try:
            template_path = os.path.join(
                os.path.dirname(__file__),
                'templates',
                self.template_name
            )
            with open(template_path, 'r') as template_file_fd:
                self.template = json.load(template_file_fd)
            return self.template
        except IOError:
            print('An IOError has occurred! path: {} file: {}'.format(
                template_path, self.template_name))

    def get_parameters(self):
        """
        Creates parameters for an Azure resource from a given dictionary object.
        :return: (dict)
        """
        if self.parameters_values:
            self.parameters = {k: {'value': v} for k, v in self.parameters_values.items()}
        else:
            self.parameters = {}
        return self.parameters

    @staticmethod
    def get_timestamp():
        """
        Create a timestamp used to create a unique name for the deployment.

        :return: (str), timestamp in the form of YYYY-MM-DD_HH.MM.SS
        """

        now = datetime.datetime.now()
        timestamp = '{}-{}-{}_{}.{}.{}'.format(now.year, now.month, now.day,
                                               now.hour, now.minute, now.second)
        return timestamp

    def deploy(self):
        """
        Deploys the template using the specified deployment properties and
        prints the name of the deployment from the name property of the
        deployment output.
        :return: (None)
        """

        self.create_resource_group()
        try:
            print('get_para: ', self.get_parameters())
            deployment_properties = {
                'mode': DeploymentMode.incremental,
                'template': self.get_template(),
                'parameters': self.get_parameters()
            }
            deployment_async_operation = self.client.deployments.create_or_update(
                self.resource_group,
                '{}_{}'.format(self.resource_group, self.get_timestamp()),
                deployment_properties
            )
            deployment_async_operation.wait()
            self.deployment_output = deployment_async_operation.result()
            print('Deployed job {}'.format(self.deployment_output.name))
        except azure_exceptions.CloudError as e:
            print(e)

    def destroy(self):
        """
        Destroy the specified resource group.

        :return: (None)
        """
        try:
            self.client.resource_groups.delete(self.resource_group)
        except azure_exceptions.CloudError as e:
            print(e)


def main():
    cloud_definition = ''
    tenant = ''
    location = ''
    subscription_id = ''
    resource_group = ''
    service_principal = ''
    secret = ''
    template_name = ''

    loader = Loader(cloud_definition, tenant, location, subscription_id,
                    resource_group, service_principal, secret, template_name)

    loader.deploy()
    print(loader)
    loader.destroy()


if __name__ == '__main__':
    main()
