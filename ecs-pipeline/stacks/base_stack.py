from aws_cdk import Stack, aws_ec2 as ec2
from constructs import Construct
from stacks.vpc.networking_stack import BasicNetworkingStack
from stacks.ec2.alb_stack import ALBStack
from stacks.ecr.ecr_stack import EcrStack     # Import your EcrStack


class BaseStack(Stack):
    def __init__(self, scope: Construct, id: str, config: dict, env_name: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.network_stack = BasicNetworkingStack(
            self,
            "BasicNetworkingStack",
            vpc_name=f"{config['PROJECT_NAME']}-{env_name}-vpc",
            vpc_cidr=config["VPC_CIDR"],
            num_public_subnets=config["NUM_PUBLIC_SUBNETS"],
            num_private_subnets=config["NUM_PRIVATE_SUBNETS"],
        )

        self.alb_stack = ALBStack(
            self,
            "ALBStack",
            vpc=self.network_stack.vpc,
            env_name=env_name,
            project_name=config["PROJECT_NAME"],
        )

        # Instantiate EcrStack and reuse repository
        self.ecr_stack = EcrStack(
            self,
            "EcrStack",
            project_name=config["PROJECT_NAME"],
            env_name=env_name,
        )

        # Export shared resources
        self.vpc = self.network_stack.vpc
        self.alb = self.alb_stack.alb
        self.listener = self.alb_stack.listener
        self.target_group = self.alb_stack.target_group
        self.repository = self.ecr_stack.repository
