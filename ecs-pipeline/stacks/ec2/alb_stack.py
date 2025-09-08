from aws_cdk import (
    NestedStack,
    aws_elasticloadbalancingv2 as elbv2,
    aws_ec2 as ec2,
    Tags,
)
from constructs import Construct


class ALBStack(NestedStack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        vpc: ec2.Vpc,
        env_name: str,
        project_name: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        alb_name = f"{project_name}-{env_name}-alb"

        # Security Group for ALB to allow HTTP traffic
        alb_sg = ec2.SecurityGroup(
            self,
            "ALBSecurityGroup",
            vpc=vpc,
            description="Security group for Application Load Balancer",
            allow_all_outbound=True,
        )
        alb_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP traffic from anywhere",
        )

        # ALB (Internet facing)
        self.alb = elbv2.ApplicationLoadBalancer(
            self,
            "ALB",
            vpc=vpc,
            internet_facing=True,
            security_group=alb_sg,
            load_balancer_name=alb_name,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )

        Tags.of(self.alb).add("Name", alb_name)

        # Listener on port 80 (HTTP)
        self.listener = self.alb.add_listener(
            "HttpListener",
            port=80,
            open=True,  # Allows connections from anywhere
        )

        # Target Group without blue-green complexity
        self.target_group = elbv2.ApplicationTargetGroup(
            self,
            "TargetGroup",
            vpc=vpc,
            target_group_name=f"{project_name}-{env_name}-tg",
            protocol=elbv2.ApplicationProtocol.HTTP,
            port=80,
            target_type=elbv2.TargetType.IP,
            # target_type=elbv2.TargetType.INSTANCE,
            health_check=elbv2.HealthCheck(path="/"),
        )

        # Attach Target Group to listener with default forwarding
        self.listener.add_target_groups(
            "DefaultTargetGroup",
            target_groups=[self.target_group],
        )
