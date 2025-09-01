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
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Modern CDK prefers ipAddresses over cidr (cidr is deprecated)
        self.vpc = ec2.Vpc(
            self,
            "Vpc",
            vpc_name=vpc_name,
            ip_addresses=ec2.IpAddresses.cidr(vpc_cidr),
            max_azs=2,  # AZ count limited by subnet counts
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
