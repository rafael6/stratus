__author__ = 'rafael'

from stratus import cirrus

# Consumer module

print(cirrus.create_vpc('MyVPC',
                       DryRun=False,
                       CidrBlock='10.73.0.0/20',
                       InstanceTenancy='default',
                       AmazonProvidedIpv6CidrBlock=False))

print(cirrus.create_subnet('FrontEnd',
                          DryRun=False,
                          VpcId='vpc-?',
                          CidrBlock='10.73.0.0/22'))

print(cirrus.create_subnet('MidTear',
                          DryRun=False,
                          VpcId='vpc-?',

                          CidrBlock='10.73.4.0/22'))

print(cirrus.create_subnet('BackEnd',
                          DryRun=False,
                          VpcId='vpc-?',
                          CidrBlock='10.73.8.0/22'))

print(cirrus.create_subnet('DMZ',
                          DryRun=False,
                          VpcId='vpc-?',
                          CidrBlock='10.73.12.0/24'))

print(cirrus.create_dhcp_options('DHCP',
                                DryRun=False,
                                DhcpConfigurations=[
                                    {
                                        'Key': 'domain-name-servers',
                                        'Values': ['10.10.0.1', '10.10.0.2']
                                    }
                                ]))

print(cirrus.create_route_table('VPC_RTB', DryRun=False, VpcId='vpc-?'))

print(cirrus.create_vpn_gateway('VPC_VGW', DryRun=False, Type='ipsec.1'))

print(cirrus.attach_vpn_gateway(DryRun=False, VpnGatewayId='vgw-?', VpcId='vpc-?'))

print(cirrus.create_customer_gateway('VPC_CGW',
                                    DryRun=False,
                                    Type='ipsec.1',
                                    PublicIp='1.1.1.1',
                                    BgpAsn=64601))


print(cirrus.create_route(DryRun=False,
                         RouteTableId='rtb-?',
                         DestinationCidrBlock='0.0.0.0/0',
                         GatewayId='vgw-6ae28249'))

print(cirrus.associate_route_table(DryRun=False, SubnetId='subnet-?', RouteTableId='rtb-?'))
print(cirrus.associate_route_table(DryRun=False, SubnetId='subnet-?', RouteTableId='rtb-?'))
print(cirrus.associate_route_table(DryRun=False, SubnetId='subnet-?', RouteTableId='rtb-?'))
print(cirrus.associate_route_table(DryRun=False, SubnetId='subnet-?', RouteTableId='rtb-?'))

print(cirrus.associate_dhcp_options(DryRun=False, DhcpOptionsId='dopt-?', VpcId='vpc-?'))


print(cirrus.enable_vgw_route_propagation(RouteTableId='rtb-?', GatewayId='vgw-?'))

# vpn-9ae888b9
vpn_connection_name = 'VPC_VPN_CONN'
connection_type = 'ipsec.1'
customer_gateway_id = 'cgw-?'
vpn_gateway_id = 'vgw-?'
options = {'StaticRoutesOnly': False}
print(cirrus.create_vpn_connection(vpn_connection_name,
                                  DryRun=False,
                                  Type=connection_type,
                                  CustomerGatewayId=customer_gateway_id,
                                  VpnGatewayId=vpn_gateway_id,
                                  Options=options))


print(cirrus.create_network_acl('VPC_ACL', DryRun=False, VpcId='vpc-?'))


print(cirrus.create_network_acl_entry(DryRun=False,
                                     NetworkAclId='acl-',
                                     RuleNumber=100,
                                     Protocol='udp',
                                     RuleAction='allow',
                                     Egress=False,
                                     CidrBlock='0.0.0.0/0',
                                     PortRange={
                                         'From': 123,
                                         'To': 123
                                     }))


print(cirrus.replace_network_acl_entry(CidrBlock='1.1.1.1/24',
                                      Egress=False,
                                      NetworkAclId='acl-?',
                                      PortRange={
                                          'From': 53,
                                          'To': 53,
                                      },
                                      Protocol='udp',
                                      RuleAction='allow',
                                      RuleNumber=110,))


print(cirrus.replace_network_acl_association(DryRun=False,
                                            AssociationId='aclassoc-?',
                                            NetworkAclId='acl-?'))

