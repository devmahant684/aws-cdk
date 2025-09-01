from aws_cdk import Stack, aws_ec2 as ec2, aws_elasticloadbalancingv2 as elbv2, aws_ecr as ecr
from constructs import Construct
from stacks.vpc.networking_stack import BasicNetworkingStack
from stacks.ec2.alb_stack import ALBStack
from stacks.ecr.ecr_stack import EcrStack


class BaseStack(Stack):
    def __init__(self, scope: Construct, id: str, config: dict, env_name: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Networking stack
        self.network_stack = BasicNetworkingStack(
            self,
            "BasicNetworkingStack",
            vpc_name=f"{config['PROJECT_NAME']}-{env_name}-vpc",
            vpc_cidr=config["VPC_CIDR"],
            num_public_subnets=config["NUM_PUBLIC_SUBNETS"],
            num_private_subnets=config["NUM_PRIVATE_SUBNETS"],
            region=config["REGION"],
        )

        # ALB stack (reads vpc from networking stack)
        self.alb_stack = ALBStack(
            self,
            "ALBStack",
            vpc=self.network_stack.vpc,
            env_name=env_name,
            project_name=config["PROJECT_NAME"],
        )

        # ECR registry stack
        self.ecr_stack = EcrStack(
            self,
            "EcrStack",
            project_name=config["PROJECT_NAME"],
            env_name=env_name,
        )

        # Export shared resources as public properties for other stacks to reference
        self.vpc = self.network_stack.vpc
        self.listener = self.alb_stack.listener
        self.blue_target_group = self.alb_stack.blue_tg
        self.green_target_group = self.alb_stack.green_tg
        self.repository = self.ecr_stack.repository
