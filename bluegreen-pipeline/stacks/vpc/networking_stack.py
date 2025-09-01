 
# from aws_cdk import (
#     NestedStack,
#     aws_ec2 as ec2,
# )
# from constructs import Construct

# class BasicNetworkingStack(NestedStack):

#     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
#         super().__init__(scope, construct_id, **kwargs)

#         # Create a VPC with public and private subnets across 2 AZs
#         self.vpc = ec2.Vpc(
#             self, "MyVpc",
#             ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
#             max_azs=2,
#             subnet_configuration=[
#                 ec2.SubnetConfiguration(
#                     name="Public",
#                     subnet_type=ec2.SubnetType.PUBLIC,
#                     cidr_mask=24,
#                 ),
#                 ec2.SubnetConfiguration(
#                     name="Private",
#                     subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
#                     cidr_mask=24,
#                 ),
#                 # Optionally add isolated subnets (e.g., for RDS or Redshift)
#                 # ec2.SubnetConfiguration(
#                 #     name="Isolated",
#                 #     subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
#                 #     cidr_mask=28,
#                 # ),
#             ],
#             nat_gateways=1,
#         )

#         # Web Tier Security Group
#         self.web_sg = ec2.SecurityGroup(
#             self, "WebSecurityGroup",
#             vpc=self.vpc,
#             description="Security group for web servers",
#             allow_all_outbound=True,
#         )
#         self.web_sg.add_ingress_rule(
#             peer=ec2.Peer.any_ipv4(),
#             connection=ec2.Port.tcp(80),
#             description="Allow HTTP traffic",
#         )
#         self.web_sg.add_ingress_rule(
#             peer=ec2.Peer.any_ipv4(),
#             connection=ec2.Port.tcp(443),
#             description="Allow HTTPS traffic",
#         )

#         # # App Tier Security Group
#         # self.app_sg = ec2.SecurityGroup(
#         #     self, "AppSecurityGroup",
#         #     vpc=self.vpc,
#         #     description="Security group for application/backend servers",
#         #     allow_all_outbound=True,
#         # )
#         # self.app_sg.add_ingress_rule(
#         #     peer=self.web_sg,
#         #     connection=ec2.Port.tcp(8080),
#         #     description="Allow traffic from web tier on port 8080",
#         # )

#         # Optional outputs (helpful for debugging or referencing)
#         # CfnOutput(self, "VpcId", value=self.vpc.vpc_id)
#         # CfnOutput(self, "WebSGId", value=self.web_sg.security_group_id)
#         # CfnOutput(self, "AppSGId", value=self.app_sg.security_group_id)





from aws_cdk import NestedStack, aws_ec2 as ec2
from constructs import Construct


class BasicNetworkingStack(NestedStack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc_name: str,
        vpc_cidr: str,
        num_public_subnets: int,
        num_private_subnets: int,
        region: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = ec2.Vpc(
            self,
            "vpc_name",
            vpc_name=vpc_name,
            cidr=vpc_cidr,
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
            ],
            nat_gateways=1,
        )
