#!/usr/bin/python3
import boto3
from botocore.exceptions import ClientError
import json

__author__ = 'rafael'
__version__ = '1'

# Producer module

# Automation for the life cycle of AWS network functions.

# Create connection
client = boto3.client('ec2')

########## VPC ##########
def describe_vpcs(**kwargs):
    '''
    Describe one or more VPCs.
    :param kwargs:
        DryRun=True|False,
        VpcIds=['string',] use VpcIds=['all'] to describe all VPCs.
    :return: Dictionary containing VPC attributes
    '''
    try:
        if kwargs['VpcIds'] == ['all']:
            response = client.describe_vpcs()
        else:
            response = client.describe_vpcs(
                DryRun=kwargs['DryRun'],
                VpcIds=kwargs['VpcIds']
            )
        return response
    except ClientError as e:
        print(e)


def create_vpc(vpc_name, **kwargs):
    '''
    Creates a VPC with the specified IPv4 CIDR block and creates a name tag for
    the vpc object.
    :param vpc_name:
    :param kwargs:
        DryRun=True|False,
        CidrBlock='string',
        InstanceTenancy='default'|'dedicated'|'host',
        AmazonProvidedIpv6CidrBlock=True|False
    :return:
    '''
    try:
        response = client.create_vpc(
            DryRun=kwargs['DryRun'],
            CidrBlock=kwargs['CidrBlock'],
            InstanceTenancy=kwargs['InstanceTenancy'],
            AmazonProvidedIpv6CidrBlock=kwargs['AmazonProvidedIpv6CidrBlock']
        )
        vpc = response.get('Vpc', 'Key not found')
        vpc_id = vpc.get('VpcId', 'Key not Found')
        # Create name tag for vpc object.
        create_tags(DryRun=False,
                    Resources=[
                        vpc_id,
                    ],
                    Tags=[
                        {
                            'Key': 'Name',
                            'Value': vpc_name,
                        },
                    ],
                    )
        return response
    except ClientError as e:
        print(e)


def describe_vpc_attribute(**kwargs):
    '''
    #Describes the specified attribute of the specified VPC.
    :param kwargs:
        DryRun=True|False,
        VpcId='string',
        Attribute='enableDnsSupport'|'enableDnsHostnames'
    :return:
    '''
    try:
        response = client.describe_vpc_attribute(
            DryRun=kwargs['DryRun'],
            VpcId=kwargs['VpcId'],
            Attribute=kwargs['Attribute']
        )
        return response
    except ClientError as e:
        print(e)


def modify_vpc_attribute(**kwargs):
    '''
    Modifies the specified attribute of the specified VPC.
    :param kwargs:
        VpcId='string',
        EnableDnsSupport={
            'Value': True|False
        },
        EnableDnsHostnames={
            'Value': True|False
        }
    :return:
    '''
    try:
        response = client.modify_vpc_attribute(
            VpcId=kwargs['VpcId'],
            EnableDnsSupport=kwargs['EnableDnsSupport'],
            EnableDnsHostnames=kwargs['EnableDnsHostnames']
        )
        return response
    except ClientError as e:
        print(e)


def delete_vpc(**kwargs):
    '''
    :param kwargs:
        DryRun=True|False,
        VpcId='string'
    :return:
    '''
    try:
        response = client.delete_vpc(
                DryRun=kwargs['DryRun'],
                VpcId=kwargs['VpcId']
            )
        return response
    except ClientError as e:
        print(e)


########## SUBNET ##########
#v2
def describe_subnets(filters=None, dry_run=False):
    """
    Describes one or more of your subnets.
    The default (no parameters) is to describes all subnets.

    Usage:
        response = describe_subnets(
            filters=[{'Name': 'vpc-id', 'Values': ['vpc-a01106c2']}]))
        print(response)

    :param filters: One or more filters (list)
        Some common filters:
            {'Name': 'vpc-id', 'Values': ['vpc-a01106c2']}
            {'Name': 'subnet-id', 'Values': ['subnet-efb8c398']}
            {'Name': 'cidrBlock', 'Values': ['10.73.0.0/22']}
            {'Name': 'tag-value', 'Values': ['EIT_Prod']}

    :param dry_run: Checks required permissions for the action (bol).
    :return:
    """
    try:
        if filters:
            response = client.describe_subnets(Filters=filters, DryRun=dry_run)
        elif not filters:
            response = client.describe_subnets(SubnetIds=[], DryRun=dry_run)
        else:
            print('Something went wrong.')
        return response
    except ClientError as e:
        print(e)

#v2
def create_subnet(vpc_id, cidr_block,
                  availability_zone='default',
                  subnet_name=None,
                  dry_run=False):
    """
    Creates a subnet in an existing VPC.

    Usage:
    response = create_subnet('vpc-?', '10.0.0.0/24',
                  availability_zone='default',
                  subnet_name=None,
                  dry_run=False):

    :param vpc_id: The ID of the VPC (str).
    :param cidr_block: Subnet in CIDR notation (str).
    :param availability_zone: Availability Zone for the subnet (str).
    :param subnet_name: Name for subnet (str).
    :param dry_run: Checks whether you have the required permissions (bol).
    :return:
    """
    try:
        if 'AvailabilityZone' is not 'default':
            response = client.create_subnet(
                DryRun=dry_run,
                VpcId=vpc_id,
                CidrBlock=cidr_block,
                AvailabilityZone=availability_zone
            )
        else:
            response = client.create_subnet(
                DryRun=dry_run,
                VpcId=vpc_id,
                CidrBlock=cidr_block
            )

        subnet = response.get('Subnet', 'Key not found')
        vpc_id = subnet.get('VpcId', 'Key not found')
        cidr_block = subnet.get('CidrBlock', 'Key not found')
        subnet_id = subnet.get('SubnetId', 'Key not found')
        if subnet_name is not None:
            create_tags(DryRun=False,
                        Resources=[
                            subnet_id,
                        ],
                        Tags=[
                            {
                                'Key': 'Name',
                                'Value': subnet_name,
                            },
                        ],
                        )
        return response
    except ClientError as e:
        print(e)

#v2
def modify_subnet_attribute(subnet_attribute, subnet_id):
    """
    Modifies a subnet attribute. You can only modify one attribute at a time.

    Usage:
    response = modify_subnet_attribute(
        MapPublicIpOnLaunch={'Value': True},
        subnet_id='subnet-abc123')

    print(response)

    :param subnet_attribute:
        AssignIpv6AddressOnCreation (dict):
        Specify true to indicate that network interfaces created in the
        specified subnet should be assigned an IPv6 address.
        Example, AssignIpv6AddressOnCreation={'Value': True|False}

        MapPublicIpOnLaunch (dict):
        Specify true to indicate that network interfaces created in the
        specified subnet should be assigned a public IPv4 address.
        Example, MapPublicIpOnLaunch={'Value': True|False}
    :param subnet_id: The ID of the subnet (str). Example, 'subnet-1a2b3c4d'
    :return: None
    """
    try:
        response = client.modify_subnet_attribute(subnet_attribute, SubnetId=subnet_id)
        return response
    except ClientError as e:
        print(e)

#v2
def delete_subnet(subnet_id, dry_run=False):
    """
    Deletes the specified subnet.

    Usage:
        response = client.delete_subnet('subnet-?')
        print(response)

    :param subnet_id: The id of the subnet (str).
    :param dry_run: Checks required permissions for the action (bol).
    :return:
    """
    try:
        response = client.delete_subnet(
            DryRun=dry_run,
            SubnetId=subnet_id
        )
        return response
    except ClientError as e:
        print(e)


########## DHCP ##########
def describe_dhcp_options(**kwargs):
    '''
    Describes one or more of your DHCP options sets.
    :param kwargs:
        DhcpOptionsIds=['string',]
        Filters=[{'Name': 'string', 'Values': ['string',]},]
        DryRun=True|False
    :return:
    '''
    try:
        if 'DhcpOptionsIds' in kwargs:
            response = client.describe_dhcp_options(
                DhcpOptionsIds=kwargs['DhcpOptionsIds'],
                DryRun=kwargs['DryRun']
            )
        elif 'Filters' in kwargs:
            response = client.describe_dhcp_options(
                Filters=kwargs['Filters'],
                DryRun=kwargs['DryRun']
            )
        return response
    except ClientError as e:
        print(e)


def create_dhcp_options(dhcp_option_name, **kwargs):
    '''
    :param dhcp_option_name:
    :param kwargs:
        'Key': 'domain-name-servers',
        'Values': ['10.2.5.1', '10.2.5.2']
    :return:
    '''
    try:
        response = client.create_dhcp_options(
            DryRun=kwargs['DryRun'],
            DhcpConfigurations=kwargs['DhcpConfigurations']
        )
        dhcp_options = response.get('DhcpOptions', 'Key not found')
        dhcp_options_id = dhcp_options.get('DhcpOptionsId', 'Key not found')
        create_tags(DryRun=False,
                    Resources=[
                        dhcp_options_id,
                    ],
                    Tags=[
                        {
                            'Key': 'Name',
                            'Value': dhcp_option_name,
                        },
                    ],
                    )

        return response
    except ClientError as e:
        print(e)


def associate_dhcp_options(**kwargs):
    '''
    Associates a set of previously created DHCP options with the specified VCP
    :param kwargs:
        DryRun=True|False,
        DhcpOptionsId='string',
        VpcId='string'
    :return: DhcpOptionsId
    '''
    try:
        response = client.associate_dhcp_options(
            DryRun=kwargs['DryRun'],
            DhcpOptionsId=kwargs['DhcpOptionsId'],
            VpcId=kwargs['VpcId']
        )
        return response
    except ClientError as e:
        print(e)


def delete_dhcp_options(**kwargs):
    '''
    Deletes the specified set of DHCP options.
    :param kwargs:
    :return:
    '''
    try:
        response = client.delete_dhcp_options(
            DryRun=kwargs['DryRun'],
            DhcpOptionsId=kwargs['DhcpOptionsId']
        )
        return json.dumps(response, indent=4)
    except ClientError as e:
        print(e)


########## INTERNET GATEWAY ##########
def describe_internet_gateways(**kwargs):
    '''
    Describes one or more of your Internet gateways using Filters or
    InternetGatewayIds.
    :param kwargs:
            DryRun=True|False
            Filters=[{'Name': 'string', 'Values': ['string',]},]
            InternetGatewayIds=['string',]
    :return:
    '''
    try:
        if 'InternetGatewayIds' in kwargs:
            response = client.describe_internet_gateways(
                DryRun=kwargs['DryRun'],
                InternetGatewayIds=kwargs['InternetGatewayIds']
            )
        elif 'Filters' in kwargs:
            response = client.describe_internet_gateways(
                DryRun=kwargs['DryRun'],
                Filters=kwargs['Filters']
            )
        else:
            print('Something went wrong.')
        return response
    except ClientError as e:
        print(e)


def create_internet_gateway(internet_gateway_name, **kwargs):
    '''
    Creates an Internet gateway for use with a VPC.
    :param name:
    :param kwargs:
        DryRun=True|False
    :return:
    '''
    try:
        response = client.create_internet_gateway(
            DryRun=kwargs['DryRun']
        )
        internet_gateway = response.get('InternetGateway', 'Key not found')
        internet_gateway_id = internet_gateway.get('InternetGatewayId')
        create_tags(DryRun=False,
                    Resources=[
                        internet_gateway_id,
                    ],
                    Tags=[
                        {
                            'Key': 'Name',
                            'Value': internet_gateway_name,
                        },
                    ],
                    )
        return response
    except ClientError as e:
        print(e)


def attach_internet_gateway(**kwargs):
    '''
    Attaches an Internet gateway to a VPC.
    :param kwargs:
        DryRun=True|False
        InternetGatewayId='string'
        VpcId='string'
    :return:
    '''
    try:
        response = client.attach_internet_gateway(
            DryRun=kwargs['DryRun'],
            InternetGatewayId=kwargs['InternetGatewayId'],
            VpcId=kwargs['VpcId']
        )
        return response
    except ClientError as e:
        print(e)


def detach_internet_gateway(**kwargs):
    '''
    Detaches an Internet gateway from a VPC.
    :param kwargs:
        DryRun=True|False,
        InternetGatewayId='string',
        VpcId='string'
    :return:
    '''
    try:
        response = client.detach_internet_gateway(
            DryRun=kwargs['DryRun'],
            InternetGatewayId=kwargs['InternetGatewayId'],
            VpcId=kwargs['VpcId']
        )
        return response
    except ClientError as e:
        print(e)


def delete_internet_gateway(**kwargs):
    '''
    Deletes the specified Internet gateway.
    :param kwargs:
        DryRun=True|False,
        InternetGatewayId='string'
    :return:
    '''
    try:
        response = client.delete_internet_gateway(
            DryRun=kwargs['DryRun'],
            InternetGatewayId=kwargs['InternetGatewayId']
        )
        return response
    except ClientError as e:
        print(e)


########## NAT GATEWAY ##########
def describe_nat_gateways(**kwargs):
    '''
    Describes one or more of the your NAT gateways.
    :param kwargs:
        NatGatewayIds=['string',]
        Filters=[{'Name': 'string', 'Values': ['string',]},],
    :return:
    '''
    try:
        if 'NatGatewayIds' in kwargs:
            response = client.describe_nat_gateways(
                NatGatewayIds=kwargs['NatGatewayIds']
            )
        elif 'Filters' in kwargs:
            response = client.describe_nat_gateways(
                Filters=kwargs['Filters']
            )
        else:
            print('Something went wrong.')

        return response
    except ClientError as e:
        print(e)


def create_nat_gateway(nat_gateway_name, **kwargs):
    '''
    Creates a NAT gateway in the specified subnet.
    :param kwargs:
        SubnetId='string'
        AllocationId='string'
        ClientToken='string'
    :return:
    '''
    try:
        response = client.create_nat_gateway(
            SubnetId=kwargs['SubnetId'],
            AllocationId=kwargs['AllocationId']
        )
        nat_gateway = response.get('NatGateway', 'Key not found')
        nat_gateway_id = nat_gateway.get('NatGatewayId', 'Key not found')
        create_tags(DryRun=False,
                    Resources=[
                        nat_gateway_id,
                    ],
                    Tags=[
                        {
                            'Key': 'Name',
                            'Value': nat_gateway_name,
                        },
                    ],
                    )
        return response
    except ClientError as e:
        print(e)


def delete_nat_gateway(**kwargs):
    '''
    Deletes the specified NAT gateway.
    :param kwargs:
        NatGatewayId='string'
    :return:
    '''
    try:
        response = client.delete_nat_gateway(
            NatGatewayId=kwargs['NatGatewayId']
        )
        return response
    except ClientError as e:
        print(e)


########## CUSTOMER GATEWAY ##########
def describe_customer_gateways(**kwargs):
    '''
    Provides information to AWS about your VPN customer gateway device.
    Describes one or more of your VPN customer gateways.
    :param kwargs:
        DryRun=True|False,
        CustomerGatewayIds=['string',]
        Filters=[{'Name': 'string', 'Values': ['string',]},]
    :return:
    '''
    try:
        if 'CustomerGatewayIds' in kwargs:
            response = client.describe_customer_gateways(
                DryRun=kwargs['DryRun'],
                CustomerGatewayIds=kwargs['CustomerGatewayIds']
            )
        elif 'Filters' in kwargs:
            response = client.describe_customer_gateways(
                DryRun=kwargs['DryRun'],
                Filters=kwargs['Filters']
            )
        else:
            print('Something went wrong.')
        return response
    except ClientError as e:
        print(e)


def create_customer_gateway(customer_gateway_name, **kwargs):
    '''
    Provides information to AWS about your VPN customer gateway device.
    :param kwargs:
        DryRun=True|False,
        Type='ipsec.1',
        PublicIp='string',
        BgpAsn=123
    :return:
    '''
    response = client.create_customer_gateway(
        DryRun=kwargs['DryRun'],
        Type=kwargs['Type'],
        PublicIp=kwargs['PublicIp'],
        BgpAsn=kwargs['BgpAsn']
    )
    customer_gateway = response.get('CustomerGateway', 'Key not found')
    customer_gateway_id = customer_gateway.get('CustomerGatewayId', 'Key not Found')
    # Create name tag for vpc object.
    create_tags(DryRun=False,
                Resources=[
                    customer_gateway_id,
                ],
                Tags=[
                    {
                        'Key': 'Name',
                        'Value': customer_gateway_name,
                    },
                ],
                )
    return response


def delete_customer_gateway(**kwargs):
    '''
    Deletes the specified customer gateway.
    :param kwargs:
        DryRun=True|False,
        CustomerGatewayId='string'
    :return:
    '''
    try:
        response = client.delete_customer_gateway(
            DryRun=kwargs['DryRun'],
            CustomerGatewayId=kwargs['CustomerGatewayId']
        )
        return response
    except ClientError as e:
        print(e)


########## VPN GATEWAY ##########
def describe_vpn_gateways(**kwargs):
    '''
    Describes one or more of your virtual private gateways.
    :param kwargs:
        DryRun=True|False,
        VpnGatewayIds=['string',]
        Filters=[{'Name': 'string', 'Values': ['string',]},]
    :return:
    '''
    if 'VpnGatewayIds' in kwargs:
        response = client.describe_vpn_gateways(
            DryRun=kwargs['DryRun'],
            VpnGatewayIds=kwargs['VpnGatewayIds']
        )
    elif 'Filters' in kwargs:
        response = client.describe_vpn_gateways(
            DryRun=kwargs['DryRun'],
            Filters=kwargs['Filters']
        )
    else:
        print('Something went wrong.')
    return response


def create_vpn_gateway(vpn_gateway_name, **kwargs):
    '''
    Creates a virtual private gateway.
    :param kwargs:
        DryRun=True|False,
        Type='ipsec.1',
        AvailabilityZone='string'
    :return:
    '''
    try:
        if 'AvailabilityZone' in kwargs:
            response = client.create_vpn_gateway(
                DryRun=kwargs['DryRun'],
                Type=kwargs['Type'],
                AvailabilityZone=kwargs['AvailabilityZone']
            )
        else:
            response = client.create_vpn_gateway(
                DryRun=kwargs['DryRun'],
                Type=kwargs['Type']
            )

        vpn_gateway = response.get('VpnGateway', 'Key not found')
        vpn_gateway_id = vpn_gateway.get('VpnGatewayId', 'Key not found')
        create_tags(DryRun=False,
                    Resources=[
                        vpn_gateway_id,
                    ],
                    Tags=[
                        {
                            'Key': 'Name',
                            'Value': vpn_gateway_name,
                        },
                    ],
                    )
        return response
    except ClientError as e:
        print(e)


def attach_vpn_gateway(**kwargs):
    '''
    Attaches a virtual private gateway to a VPC.
    :param kwargs:
        DryRun=True|False,
        VpnGatewayId='string',
        VpcId='string'
    :return:
    '''
    try:
        response = client.attach_vpn_gateway(
            DryRun=kwargs['DryRun'],
            VpnGatewayId=kwargs['VpnGatewayId'],
            VpcId=kwargs['VpcId']
        )
        return response
    except ClientError as e:
        print(e)


def detach_vpn_gateway(**kwargs):
    '''
    Detaches a virtual private gateway from a VPC.
    :param kwargs:
        DryRun=True|False,
        VpnGatewayId='string',
        VpcId='string'
    :return:
    '''
    try:
        response = client.detach_vpn_gateway(
            DryRun=kwargs['DryRun'],
            VpnGatewayId=kwargs['VpnGatewayId'],
            VpcId=kwargs['VpcId']
        )
        return response
    except ClientError as e:
        print(e)


def enable_vgw_route_propagation(**kwargs):
    '''
    Enables a virtual private gateway (VGW) to propagate routes to the
    specified route table of a VPC.
    :param kwargs:
        RouteTableId='string',
        GatewayId='string'
    :return:
    '''
    response = client.enable_vgw_route_propagation(
        RouteTableId=kwargs['RouteTableId'],
        GatewayId=kwargs['GatewayId']
    )
    return response


def disable_vgw_route_propagation(**kwargs):
    '''
    Disables a virtual private gateway (VGW) from propagating routes to a
    specified route table of a VPC.
    :param kwargs:
        RouteTableId='string',
        GatewayId='string'
    :return:
    '''
    try:
        response = client.disable_vgw_route_propagation(
            RouteTableId=kwargs['RouteTableId'],
            GatewayId=kwargs['GatewayId']
        )
        return response
    except ClientError as e:
        print(e)


def delete_vpn_gateway(**kwargs):
    '''
    Deletes the specified virtual private gateway.
    :param kwargs:
        DryRun=True|False,
        VpnGatewayId='string'
    :return:
    '''
    try:
        response = client.delete_vpn_gateway(
            DryRun=kwargs['DryRun'],
            VpnGatewayId=kwargs['VpnGatewayId']
        )
        return response
    except ClientError as e:
        print(e)


########## VPN CONNECTION ##########
def describe_vpn_connections(**kwargs):
    '''
    Describes one or more of your VPN connections.
    :param kwargs:
        DryRun=True|False,
        VpnConnectionIds=['string']
        Filters=[{'Name': 'string', 'Values': ['string',]},]
    :return:
    '''
    try:
        if 'VpnConnectionIds' in kwargs:
            response = client.describe_vpn_connections(
                DryRun=kwargs['DryRun'],
                VpnConnectionIds=kwargs['VpnConnectionIds'])
        elif 'Filters' in kwargs:
            response = client.describe_vpn_connections(
                DryRun=kwargs['DryRun'],
                Filters=kwargs['Filters'])
        else:
            print('Something went wrong.')
        return response
    except ClientError as e:
        print(e)


def create_vpn_connection(vpn_connection_name, **kwargs):
    '''
    Creates a VPN connection between an existing virtual private gateway and a VPN customer gateway.
    :param kwargs:
    :return:
        DryRun=True|False,
        Type='string',
        CustomerGatewayId='string',
        VpnGatewayId='string',
        Options={'StaticRoutesOnly': True|False}
    '''
    try:
        response = client.create_vpn_connection(
            DryRun=kwargs['DryRun'],
            Type=kwargs['Type'],
            CustomerGatewayId=kwargs['CustomerGatewayId'],
            VpnGatewayId=kwargs['VpnGatewayId'],
            Options=kwargs['Options']
        )
        vpn_connection = response.get('VpnConnection', 'Key not found')
        vpn_connection_id = vpn_connection.get('VpnConnectionId', 'Key not found')
        create_tags(DryRun=False,
                    Resources=[
                        vpn_connection_id,
                    ],
                    Tags=[
                        {
                            'Key': 'Name',
                            'Value': vpn_connection_name,
                        },
                    ],
                    )

        return response
    except ClientError as e:
        print(e)


def delete_vpn_connection(**kwargs):
    '''
    Deletes the specified VPN connection.
    :param kwargs:
        DryRun=True|False,
        VpnConnectionId='string'
    :return:
    '''
    try:
        response = client.delete_vpn_connection(
            DryRun=kwargs['DryRun'],
            VpnConnectionId=kwargs['VpnConnectionId']
        )
        return response
    except ClientError as e:
        print(e)


def create_vpn_connection_route(**kwargs):
    '''
    Creates a static route associated with a VPN connection between an existing
    virtual private gateway and a VPN customer gateway.
    :param kwargs:
        VpnConnectionId='string',
        DestinationCidrBlock='string'
    :return:
    '''
    try:
        response = client.create_vpn_connection_route(
            VpnConnectionId=kwargs['VpnConnectionId'],
            DestinationCidrBlock=kwargs['DestinationCidrBlock']
        )
        return response
    except ClientError as e:
        print(e)


def delete_vpn_connection_route(**kwargs):
    '''
    Deletes the specified static route associated with a VPN connection between
    an existing virtual private gateway and a VPN customer gateway.
    :param kwargs:
        VpnConnectionId='string',
        DestinationCidrBlock='string'
    :return:
    '''
    try:
        response = client.delete_vpn_connection_route(
            VpnConnectionId=kwargs['VpnConnectionId'],
            DestinationCidrBlock=kwargs['DestinationCidrBlock']
        )
        return response
    except ClientError as e:
        print(e)


########## ROUTE ##########
def describe_route_tables(**kwargs):
    '''
    Describes one or more of your route tables.
    :param kwargs:
        DryRun=True|False,
        RouteTableIds=['string',]
        Filters=[{'Name': 'string', 'Values': ['string',]},]
    :return:
    '''
    try:
        if 'RouteTableIds' in kwargs:
            response = client.describe_route_tables(
                DryRun=kwargs['DryRun'],
                RouteTableIds=kwargs['RouteTableIds']
            )
        elif 'Filters' in kwargs:
            response = client.describe_route_tables(
                DryRun=kwargs['DryRun'],
                Filters=kwargs['Filters']
            )
        else:
            print('Something went wrong.')
        return response
    except ClientError as e:
        print(e)


def create_route_table(route_table_name, **kwargs):
    '''
    Creates a route table for the specified VPC.
    :param kwargs:
        DryRun=True|False,
        VpcId='string'

    :return:
    '''
    try:
        response = client.create_route_table(
            DryRun=kwargs['DryRun'],
            VpcId=kwargs['VpcId']
        )
        route_tabe = response.get('RouteTable', 'Key not found')
        route_table_id = route_tabe.get('RouteTableId', 'Key not Found')
        # Create name tag for object.
        create_tags(DryRun=False,
                    Resources=[
                        route_table_id,
                    ],
                    Tags=[
                        {
                            'Key': 'Name',
                            'Value': route_table_name,
                        },
                    ],
                    )
        return response
    except ClientError as e:
        print(e)


def disassociate_route_table(**kwargs):
    '''
    Disassociates a subnet from a route table.
    :param kwargs:
        DryRun=True|False,
        AssociationId='string'
    :return:
    '''
    try:
        response = client.disassociate_route_table(
            DryRun=kwargs['DryRun'],
            AssociationId=kwargs['AssociationId']
        )
        return response
    except ClientError as e:
        print(e)


def associate_route_table(**kwargs):
    '''
    Associates a subnet with a route table.
    :param kwargs:
        DryRun=True|False,
        SubnetId='string',
        RouteTableId='string'
    :return:
    '''
    try:
        response = client.associate_route_table(
            DryRun=kwargs['DryRun'],
            SubnetId=kwargs['SubnetId'],
            RouteTableId=kwargs['RouteTableId']
        )
        return response
    except ClientError as e:
        print(e)


def replace_route_table_association(**kwargs):
    '''
    Changes the route table associated with a given subnet in a VPC.
    :param kwargs:
        DryRun=True|False,
        AssociationId='string',
        RouteTableId='string'
    :return:
    '''
    try:
        response = client.replace_route_table_association(
            DryRun=kwargs['DryRun'],
            AssociationId=kwargs['AssociationId'],
            RouteTableId=kwargs['RouteTableId']
        )
        return response
    except ClientError as e:
        print(e)


def delete_route_table(**kwargs):
    '''
    # Deletes the specified route table.
    :param kwargs:
       DryRun=True|False,
        RouteTableId='string'
    :return:
    '''
    try:
        response = client.delete_route_table(
            DryRun=kwargs['DryRun'],
            RouteTableId=kwargs['RouteTableId']
        )
        return response
    except ClientError as e:
        print(e)


def create_route(**kwargs):
    '''
    Creates a route in a route table within a VPC.
    :param kwargs:
        DryRun=True|False,
        RouteTableId='string',
        DestinationCidrBlock='string',
        GatewayId='string',
        DestinationIpv6CidrBlock='string',
        EgressOnlyInternetGatewayId='string',
        InstanceId='string',
        NetworkInterfaceId='string',
        VpcPeeringConnectionId='string',
        NatGatewayId='string'
    :return:
    '''
    try:
        if 'GatewayId' in kwargs:
            response = client.create_route(
                DryRun=kwargs['DryRun'],
                RouteTableId=kwargs['RouteTableId'],
                DestinationCidrBlock=kwargs['DestinationCidrBlock'],
                GatewayId=kwargs['GatewayId'],
            )
        elif 'InstanceId' in kwargs:
            response = client.create_route(
                DryRun=kwargs['DryRun'],
                RouteTableId=kwargs['RouteTableId'],
                DestinationCidrBlock=kwargs['DestinationCidrBlock'],
                InstanceId=kwargs['InstanceId']
            )
        elif 'EgressOnlyInternetGatewayId' in kwargs:
            response = client.create_route(
                DryRun=kwargs['DryRun'],
                RouteTableId=kwargs['RouteTableId'],
                DestinationCidrBlock=kwargs['DestinationCidrBlock'],
                EgressOnlyInternetGatewayId=kwargs['EgressOnlyInternetGatewayId']
            )
        elif 'NetworkInterfaceId' in kwargs:
            response = client.create_route(
                DryRun=kwargs['DryRun'],
                RouteTableId=kwargs['RouteTableId'],
                DestinationCidrBlock=kwargs['DestinationCidrBlock'],
                NetworkInterfaceId=kwargs['NetworkInterfaceId']
            )
        elif 'VpcPeeringConnectionId' in kwargs:
            response = client.create_route(
                DryRun=kwargs['DryRun'],
                RouteTableId=kwargs['RouteTableId'],
                DestinationCidrBlock=kwargs['DestinationCidrBlock'],
                VpcPeeringConnectionId=kwargs['VpcPeeringConnectionId']
            )
        elif 'NatGatewayId' in kwargs:
            response = client.create_route(
                DryRun=kwargs['DryRun'],
                RouteTableId=kwargs['RouteTableId'],
                DestinationCidrBlock=kwargs['DestinationCidrBlock'],
                NatGatewayId=kwargs['NatGatewayId']
            )
        elif 'DestinationIpv6CidrBlock' in kwargs:
            response = client.create_route(
                DryRun=kwargs['DryRun'],
                RouteTableId=kwargs['RouteTableId'],
                DestinationIpv6CidrBlock=kwargs['DestinationIpv6CidrBlock'],
                EgressOnlyInternetGatewayId=kwargs['EgressOnlyInternetGatewayId']
            )
        return response
    except ClientError as e:
        print(e)


def delete_route(**kwargs):
    '''
    Deletes a specified route from the specified route table.
    :param kwargs:
        DryRun=True|False,
        RouteTableId='string',
        DestinationCidrBlock='string',
        DestinationIpv6CidrBlock='string'
    :return:
    '''
    try:
        if 'DestinationIpv6CidrBlock' in kwargs:
            response = client.delete_route(
                DryRun=kwargs['DryRun'],
                RouteTableId=kwargs['RouteTableId'],
                DestinationIpv6CidrBlock=kwargs['DestinationIpv6CidrBlock']
            )
        else:
            response = client.delete_route(
                DryRun=kwargs['DryRun'],
                RouteTableId=kwargs['RouteTableId'],
                DestinationCidrBlock=kwargs['DestinationCidrBlock']
            )
        return response
    except ClientError as e:
        print(e)


def replace_route(**kwargs):
    '''
    Replaces an existing route within a route table in a VPC.
    :param kwargs:
         DryRun=True|False,
        RouteTableId='string',
        DestinationCidrBlock='string',
        GatewayId='string',
        DestinationIpv6CidrBlock='string',
        EgressOnlyInternetGatewayId='string',
        InstanceId='string',
        NetworkInterfaceId='string',
        VpcPeeringConnectionId='string',
        NatGatewayId='string'
    :return:
    '''
    try:
        if 'GatewayId' in kwargs:
            response = client.replace_route(
                DryRun=kwargs['DryRun'],
                RouteTableId=kwargs['RouteTableId'],
                DestinationCidrBlock=kwargs['DestinationCidrBlock'],
                GatewayId=kwargs['GatewayId']
            )
        elif 'InstanceId' in kwargs:
            response = client.replace_route(
                DryRun=kwargs['DryRun'],
                RouteTableId=kwargs['RouteTableId'],
                DestinationCidrBlock=kwargs['DestinationCidrBlock'],
                InstanceId=kwargs['InstanceId']
            )
        elif 'NetworkInterfaceId' in kwargs:
            response = client.replace_route(
                DryRun=kwargs['DryRun'],
                RouteTableId=kwargs['RouteTableId'],
                DestinationCidrBlock=kwargs['DestinationCidrBlock'],
                NetworkInterfaceId=kwargs['NetworkInterfaceId']
            )
        elif 'VpcPeeringConnectionId' in kwargs:
            response = client.replace_route(
                DryRun=kwargs['DryRun'],
                RouteTableId=kwargs['RouteTableId'],
                DestinationCidrBlock=kwargs['DestinationCidrBlock'],
                VpcPeeringConnectionId=kwargs['VpcPeeringConnectionId']
            )
        elif 'NatGatewayId' in kwargs:
            response = client.replace_route(
                DryRun=kwargs['DryRun'],
                RouteTableId=kwargs['RouteTableId'],
                DestinationCidrBlock=kwargs['DestinationCidrBlock'],
                NatGatewayId=kwargs['NatGatewayId']
            )
        elif 'DestinationIpv6CidrBlock' in kwargs:
            response = client.replace_route(
                DryRun=kwargs['DryRun'],
                RouteTableId=kwargs['RouteTableId'],
                DestinationIpv6CidrBlock=kwargs['DestinationIpv6CidrBlock'],
                EgressOnlyInternetGatewayId=kwargs['EgressOnlyInternetGatewayId']
            )
        return response
    except ClientError as e:
        print(e)


########## ACL ##########
def describe_network_acls(**kwargs):
    '''
    Describes one or more of your network ACLs.
    :param kwargs:
        DryRun=True|False,
        NetworkAclIds=['string']
        Filters=[{'Name': 'string', 'Values': ['string',]},]
    :return:
    '''
    try:
        if 'NetworkAclIds' in kwargs:
            response = client.describe_network_acls(
                DryRun=kwargs['DryRun'],
                NetworkAclIds=kwargs['NetworkAclIds']
            )
        elif 'Filters' in kwargs:
            response = client.describe_network_acls(
                DryRun=kwargs['DryRun'],
                Filters=kwargs['Filters']
            )
        else:
            print('Something went wrong.')
        return response
    except ClientError as e:
        print(e)


def create_network_acl(network_acl_name, **kwargs):
    '''
    Creates a network ACL in a VPC.
    :param kwargs:
        DryRun=True|False,
        VpcId='string'
    :return:
    '''
    try:
        response = client.create_network_acl(
            DryRun=kwargs['DryRun'],
            VpcId=kwargs['VpcId']
        )
        network_acl = response.get('NetworkAcl', 'Key not found')
        network_acl_id = network_acl.get('NetworkAclId', 'Key not found')
        create_tags(DryRun=False,
                    Resources=[
                        network_acl_id,
                    ],
                    Tags=[
                        {
                            'Key': 'Name',
                            'Value': network_acl_name,
                        },
                    ],
                    )

        return response
    except ClientError as e:
        print(e)


def create_network_acl_entry(**kwargs):
    '''
    Creates an entry (a rule) in a network ACL with the specified rule number.
    :param kwargs:
        DryRun=True|False,
        NetworkAclId='string',
        RuleNumber=123,
        Protocol='string',
        RuleAction='allow'|'deny',
        Egress=True|False,
        CidrBlock='string',
        Ipv6CidrBlock='string',
        IcmpTypeCode={'Type': 123, 'Code': 123},
        PortRange={'From': 123, 'To': 123}
    :return:
    '''
    try:
        if 'Ipv6CidrBlock' not in kwargs and 'IcmpTypeCode' not in kwargs:
            response = client.create_network_acl_entry(
                DryRun=kwargs['DryRun'],
                NetworkAclId=kwargs['NetworkAclId'],
                RuleNumber=kwargs['RuleNumber'],
                Protocol=kwargs['Protocol'],
                RuleAction=kwargs['RuleAction'],
                Egress=kwargs['Egress'],
                CidrBlock=kwargs['CidrBlock'],
                PortRange=kwargs['PortRange']
            )
        elif 'Ipv6CidrBlock' not in kwargs and 'IcmpTypeCode' in kwargs:
            response = client.create_network_acl_entry(
                DryRun=kwargs['DryRun'],
                NetworkAclId=kwargs['NetworkAclId'],
                RuleNumber=kwargs['RuleNumber'],
                Protocol=kwargs['Protocol'],
                RuleAction=kwargs['RuleAction'],
                Egress=kwargs['Egress'],
                CidrBlock=kwargs['CidrBlock'],
                IcmpTypeCode=kwargs['IcmpTypeCode'],
                PortRange=kwargs['PortRange']
            )
        elif 'Ipv6CidrBlock' in kwargs:
            response = client.create_network_acl_entry(
                DryRun=kwargs['DryRun'],
                NetworkAclId=kwargs['NetworkAclId'],
                RuleNumber=kwargs['RuleNumber'],
                Protocol=kwargs['Protocol'],
                RuleAction=kwargs['RuleAction'],
                Egress=kwargs['Egress'],
                Ipv6CidrBlock=kwargs['Ipv6CidrBlock'],
                PortRange=kwargs['PortRange']
            )
        return response
    except ClientError as e:
        print(e)


def delete_network_acl(**kwargs):
    '''
    Deletes the specified network ACL.
    :param kwargs:
        DryRun=True|False,
        NetworkAclId='string'
    :return:
    '''
    try:
        response = client.delete_network_acl(
            DryRun=kwargs['DryRun'],
            NetworkAclId=kwargs['NetworkAclId']
        )
        return response
    except ClientError as e:
        print(e)


def replace_network_acl_association(**kwargs):
    '''
    Changes which network ACL a subnet is associated with.
    :param kwargs:
        DryRun=True|False,
        AssociationId='string',
        NetworkAclId='string'
    :return:
    '''
    try:
        response = client.replace_network_acl_association(
            DryRun=kwargs['DryRun'],
            AssociationId=kwargs['AssociationId'],
            NetworkAclId=kwargs['NetworkAclId']
        )
        return response
    except ClientError as e:
        print(e)


def replace_network_acl_entry(**kwargs):
    '''
    Replaces an entry (rule) in a network ACL.
    :param kwargs:
    :return:
        DryRun=True|False,
        NetworkAclId='string',
        RuleNumber=123,
        Protocol='string',
        RuleAction='allow'|'deny',
        Egress=True|False,
        CidrBlock='string',
        Ipv6CidrBlock='string',
        IcmpTypeCode={'Type': 123, 'Code': 123},
        PortRange={'From': 123, 'To': 123}
    '''
    try:
        if 'Ipv6CidrBlock' not in kwargs and 'IcmpTypeCode' not in kwargs:
            response = client.create_network_acl_entry(
                DryRun=kwargs['DryRun'],
                NetworkAclId=kwargs['NetworkAclId'],
                RuleNumber=kwargs['RuleNumber'],
                Protocol=kwargs['Protocol'],
                RuleAction=kwargs['RuleAction'],
                Egress=kwargs['Egress'],
                CidrBlock=kwargs['CidrBlock'],
                PortRange=kwargs['PortRange']
            )
        elif 'Ipv6CidrBlock' not in kwargs and 'IcmpTypeCode' in kwargs:
            response = client.create_network_acl_entry(
                DryRun=kwargs['DryRun'],
                NetworkAclId=kwargs['NetworkAclId'],
                RuleNumber=kwargs['RuleNumber'],
                Protocol=kwargs['Protocol'],
                RuleAction=kwargs['RuleAction'],
                Egress=kwargs['Egress'],
                CidrBlock=kwargs['CidrBlock'],
                IcmpTypeCode=kwargs['IcmpTypeCode'],
                PortRange=kwargs['PortRange']
            )
        elif 'Ipv6CidrBlock' in kwargs:
            response = client.create_network_acl_entry(
                DryRun=kwargs['DryRun'],
                NetworkAclId=kwargs['NetworkAclId'],
                RuleNumber=kwargs['RuleNumber'],
                Protocol=kwargs['Protocol'],
                RuleAction=kwargs['RuleAction'],
                Egress=kwargs['Egress'],
                Ipv6CidrBlock=kwargs['Ipv6CidrBlock'],
                PortRange=kwargs['PortRange']
            )
        return response
    except ClientError as e:
        print(e)


########## PEERING ##########

def describe_vpc_peering_connections(**kwargs):
    '''
    Describes one or more of your VPC peering connections.
    :param kwargs:
        DryRun=True|False
        VpcPeeringConnectionIds=['string',]
        Filters=[{'Name': 'string', 'Values': ['string',]},]
    :return:
    '''
    try:
        if 'VpcPeeringConnectionIds' in kwargs:
            response = client.describe_vpc_peering_connections(
                DryRun=kwargs['DryRun'],
                VpcPeeringConnectionIds=kwargs['VpcPeeringConnectionIds']
            )
        elif 'Filters' in kwargs:
            response = client.describe_vpc_peering_connections(
                DryRun=kwargs['DryRun'],
                Filters=kwargs['Filters']
            )
        return response
    except ClientError as e:
        print(e)


def create_vpc_peering_connection(peering_name, **kwargs):
    '''
    Requests a VPC peering connection between two VPCs
    :param kwargs:
        DryRun=True|False
        VpcId='string'
        PeerVpcId='string'
        PeerOwnerId='string'
    :return:
    '''
    try:
        response = client.create_vpc_peering_connection(
            DryRun=kwargs['DryRun'],
            VpcId=kwargs['VpcId'],
            PeerVpcId=kwargs['PeerVpcId'],
            PeerOwnerId=kwargs['PeerOwnerId']
        )
        vpc_peering_connection = response.get('VpcPeeringConnection', 'Key not found')
        vpc_peering_connection_id = vpc_peering_connection.get('VpcPeeringConnectionId', 'Key not found')
        create_tags(DryRun=False,
                    Resources=[
                        vpc_peering_connection_id,
                    ],
                    Tags=[
                        {
                            'Key': 'Name',
                            'Value': peering_name,
                        },
                    ],
                    )

        return response
    except ClientError as e:
        print(e)


def accept_vpc_peering_connection(**kwargs):
    '''
    Accept a VPC peering connection request.
    :param kwargs:
        DryRun=True|False
        VpcPeeringConnectionId='string'
    :return:
    '''
    try:
        response = client.accept_vpc_peering_connection(
            DryRun=kwargs['DryRun'],
            VpcPeeringConnectionId=kwargs['VpcPeeringConnectionId']
        )
        return response
    except ClientError as e:
        print(e)


def reject_vpc_peering_connection(**kwargs):
    '''
    Rejects a VPC peering connection request.
    :param kwargs:
        DryRun=True|False
        VpcPeeringConnectionId='string'
    :return:
    '''
    try:
        response = client.reject_vpc_peering_connection(
            DryRun=kwargs['DryRun'],
            VpcPeeringConnectionId=kwargs['VpcPeeringConnectionId']
        )
        return response
    except ClientError as e:
        print(e)


def modify_vpc_peering_connection_options(**kwargs):
    '''
    Modifies the VPC peering connection options on one side of a VPC peering connection.
    :param kwargs:
        DryRun=True|False
        VpcPeeringConnectionId='string'
        RequesterPeeringConnectionOptions={
            'AllowEgressFromLocalClassicLinkToRemoteVpc': True|False,
            'AllowEgressFromLocalVpcToRemoteClassicLink': True|False,
            'AllowDnsResolutionFromRemoteVpc': True|False
            }
        AccepterPeeringConnectionOptions={
            'AllowEgressFromLocalClassicLinkToRemoteVpc': True|False,
            'AllowEgressFromLocalVpcToRemoteClassicLink': True|False,
            'AllowDnsResolutionFromRemoteVpc': True|False
            }
    :return:
    '''
    try:
        response = client.modify_vpc_peering_connection_options(
            DryRun=kwargs['DryRun'],
            VpcPeeringConnectionId=kwargs['VpcPeeringConnectionId'],
            RequesterPeeringConnectionOptions=kwargs['RequesterPeeringConnectionOptions'],
            AccepterPeeringConnectionOptions=kwargs['AccepterPeeringConnectionOptions']
        )
        return response
    except ClientError as e:
        print(e)


def delete_vpc_peering_connection(**kwargs):
    '''
    Deletes a VPC peering connection.
    :param kwargs:
        DryRun=True|False
        VpcPeeringConnectionId='string'
    :return:
    '''
    try:
        response = client.delete_vpc_peering_connection(
            DryRun=kwargs['DryRun'],
            VpcPeeringConnectionId=kwargs['VpcPeeringConnectionId']
        )
        return response
    except ClientError as e:
        print(e)


# General
def create_tags(**kwargs):
    '''
    Adds or overwrites one or more tags for the specified Amazon EC2 resource
    or resources.
    :param kwargs:
    :return:
    '''
    try:
        response = client.create_tags(
            DryRun=kwargs['DryRun'],
            Resources=kwargs['Resources'],
            Tags=kwargs['Tags']
        )
    except ClientError as e:
        print(e)
    return response


def main():

    exit()
    ########## VPC ##########
    print(describe_vpcs(DryRun=False, VpcIds=['vpc-0eb7696b']))

    print(create_vpc('EIT_Main_VPC',
                     DryRun=False,
                     CidrBlock='10.73.0.0/20',
                     InstanceTenancy='default',
                     AmazonProvidedIpv6CidrBlock=False
                     )
          )

    print(describe_vpc_attribute(DryRun=True|False,
                                 VpcId='string',
                                 Attribute='enableDnsSupport'|'enableDnsHostnames'
                                 )
          )

    print(modify_vpc_attribute(VpcId='string',
                               EnableDnsSupport={
                                   'Value': True|False
                               },
                               EnableDnsHostnames={
                                   'Value': True|False
                               }
                               )
          )

    print(delete_vpc(DryRun=False, VpcId='vpc-76a90813'))

    ########## SUBNETS ##########
    print(describe_subnets(filters=[{'Name': 'tag-value', 'Values': ['EIT_Prod']}], dry_run=False))
    print(describe_subnets())

    print(create_subnet('vpc-?', '10.0.0.0/24', subnet_name='MySubnetName'))

    print(modify_subnet_attribute(MapPublicIpOnLaunch={'Value': False}, subnet_id='subnet-abc123'))

    print(delete_subnet('subnet-?'))

    ########## DHCP OPTIONS ##########
    print(describe_dhcp_options(DryRun=False, DhcpOptionsIds=['dopt-?',]))
    # OR
    print(describe_dhcp_options(DryRun=False, Filters=[
        {
            'Name': 'string',
            'Values': ['string',]
        },
    ],))

    print(create_dhcp_options('dhcp_option_name',
                              DhcpConfigurations=[
                                  {
                                      'Key': 'domain-name-servers',
                                      'Values': ['10.2.5.1', '10.2.5.2']
                                  }
                              ]
                              )
          )

    print(associate_dhcp_options( DryRun=False, DhcpOptionsId='string', VpcId='string'))

    print(delete_dhcp_options(DryRun=False, DhcpOptionsId='dopt-?'))

    ########## NAT GATEWAY ##########
    print(describe_nat_gateways(NatGatewayIds=['string',]))
    # OR
    print(describe_nat_gateways(Filters=[
        {
            'Name': 'vpc-id',
            'Values': [
                'vpc-1a2b3c4d',
            ],
        },
    ]))

    print(create_nat_gateway('some_name', AllocationId='eipalloc-?', SubnetId='subnet-?'))

    print(delete_nat_gateway(NatGatewayId='nat-?'))

    ########## CUSTOMER GATEWAY ##########
    print(describe_customer_gateways(DryRun= False, CustomerGatewayIds=['cgw-?']))
    # OR
    print(describe_customer_gateways(DryRun=False, Filters=[
        {
            'Name': 'string',
            'Values': [
                'string',
            ]
        },
    ],))


    print(create_customer_gateway('My_CG', DryRun=False,
                                  Type='ipsec.1',
                                  PublicIp='string',
                                  BgpAsn=123
                                  )
          )

    print(delete_customer_gateway(DryRun=False, CustomerGatewayId='cgw-'))

    ########## VPN GATEWAY ##########
    print(describe_vpn_gateways(DryRun=False, VpnGatewayIds=['string']))
    # OR
    print(describe_vpn_gateways(DryRun=False, Filters=[
        {
            'Name': 'string',
            'Values': [
                'string',
            ]
        },
    ],))

    print(create_vpn_gateway(DryRun=False, Type='ipsec.1', AvailabilityZone='string'))

    print(attach_vpn_gateway(DryRun=False, VpnGatewayId='string', VpcId='string'))

    print(detach_vpn_gateway(DryRun=False, VpnGatewayId='string', VpcId='string'))

    print(delete_vpn_gateway(DryRun=False, VpnGatewayId='string'))

    ########## VPN CONNECTION ##########

    print(describe_vpn_connections(DryRun=False, VpnConnectionIds=['string']))
    # OR
    print(describe_vpn_connections(DryRun=False, Filters=[
        {
            'Name': 'string',
            'Values': [
                'string',
            ]
        },
    ],))

    print(create_vpn_connection('vpn_connection_name',
                                DryRun=False,
                                Type='string',
                                CustomerGatewayId='string',
                                VpnGatewayId='string',
                                Options={'StaticRoutesOnly': False}
                                )
          )

    print(delete_vpn_connection(DryRun=False, VpnConnectionId='string'))

    ########## VPN CONNECTION ROUTE ###########
    print(create_vpn_connection_route(VpnConnectionId='string',
                                      DestinationCidrBlock='string')
          )

    print(delete_vpn_connection_route(VpnConnectionId='string',
                                      DestinationCidrBlock='string')
          )

    ########## ROUTE ##########
    print(describe_route_tables(DryRun=False, RouteTableIds=['string']))
    # OR
    print(describe_route_tables(DryRun=False, Filters=[
        {
            'Name': 'string',
            'Values': [
                'string',
            ]
        },
    ],))

    print(create_route_table('EIT_Main_VPC_RTB', DryRun=False, VpcId='string'))

    print(associate_route_table(DryRun=False, SubnetId='string', RouteTableId='string'))

    print(disassociate_route_table(DryRun=False, AssociationId='string'))

    print(create_route(DryRun=False,
                RouteTableId='rtb-?',
                DestinationCidrBlock='0.0.0.0/0',
                GatewayId='?'
                       )
          )

    print(delete_route(DryRun=False,
                       RouteTableId='rtb-?',
                       DestinationCidrBlock='0.0.0.0/0'
                       )
          )

    print(replace_route(DryRun=False,
                        RouteTableId='string',
                        DestinationCidrBlock='0.0.0.0/0',
                        GatewayId='?'
                        )
          )

    print(replace_route_table_association(DryRun=False,
                                          AssociationId='rtbassoc-?',
                                          RouteTableId='rtb-?'
                                          )
          )

    print(delete_route_table(DryRun=False, RouteTableId='rtb-?'))

    print(enable_vgw_route_propagation(RouteTableId='rtb-?',
                                       GatewayId='string'
                                       )
          )


    print(disable_vgw_route_propagation(RouteTableId='rtb-?',
                                        GatewayId='string'
                                        )
          )

    ########## ACL ##########
    print(describe_network_acls(DryRun=False, NetworkAclIds=['acl-?']))
    # OR
    print(describe_network_acls(DryRun=False, Filters=[
        {
            'Name': 'string',
            'Values': [
                'string',
            ]
        },
    ],))

    print(create_network_acl('network_acl_name', DryRun=False, VpcId='vpc-?'))

    print(create_network_acl_entry(DryRun=False,
                                   NetworkAclId='acl-',
                                   RuleNumber=100,
                                   Protocol='udp',
                                   RuleAction='allow',
                                   Egress=False,
                                   CidrBlock='0.0.0.0/0',
                                   PortRange={
                                       'From': 123,
                                       'To': 123
                                   }
                                   )
          )

    print(delete_network_acl(DryRun=False, NetworkAclId='acl-?'))

    print(replace_network_acl_association(DryRun=False,
                                          AssociationId='aclassoc-?',
                                          NetworkAclId='acl-?')
          )

    print(replace_network_acl_entry(CidrBlock='203.0.113.12/24',
                                    Egress=False,
                                    NetworkAclId='acl-?',
                                    PortRange={
                                        'From': 53,
                                        'To': 53,
                                    },
                                    Protocol='udp',
                                    RuleAction='allow',
                                    RuleNumber=110,
                                    )
          )

    ########## INTERNET GATEWAY ##########
    print(describe_internet_gateways(DryRun=False, InternetGatewayIds=['igw-?']))
    # OR
    print(describe_internet_gateways(DryRun=False, Filters=[
        {
            'Name': 'attachment.vpc-id',
            'Values': [
                'vpc-?',
            ],
        },
    ]))

    print(create_internet_gateway('some_name', DryRun=False))

    print(attach_internet_gateway(DryRun=False, InternetGatewayId='igw-?', VpcId='vpc-?'))

    print(detach_internet_gateway(DryRun=False, InternetGatewayId='igw-?', VpcId='vpc-?'))

    print(delete_internet_gateway(DryRun=False, InternetGatewayId='igw-?'))

    ########## PEERING ##########

    print(describe_vpc_peering_connections(DryRun=False, VpcPeeringConnectionIds='some_id'))

    print(create_vpc_peering_connection(DryRun=True|False,
                                        VpcId='string',
                                        PeerVpcId='string',
                                        PeerOwnerId='string'))

    print(accept_vpc_peering_connection(DryRun=False, VpcPeeringConnectionId='some_id'))

    print(reject_vpc_peering_connection(DryRun=False, VpcPeeringConnectionId='string'))

    print(modify_vpc_peering_connection_options(DryRun=True|False,
                                                VpcPeeringConnectionId='string',
                                                RequesterPeeringConnectionOptions={
                                                    'AllowEgressFromLocalClassicLinkToRemoteVpc': True|False,
                                                    'AllowEgressFromLocalVpcToRemoteClassicLink': True|False,
                                                    'AllowDnsResolutionFromRemoteVpc': True|False
                                                },
                                                AccepterPeeringConnectionOptions={
                                                    'AllowEgressFromLocalClassicLinkToRemoteVpc': True|False,
                                                    'AllowEgressFromLocalVpcToRemoteClassicLink': True|False,
                                                    'AllowDnsResolutionFromRemoteVpc': True|False}
                                                ))

    print(delete_vpc_peering_connection(DryRun=False, VpcPeeringConnectionId='string'))





