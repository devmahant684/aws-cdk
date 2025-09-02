from aws_cdk import (
    NestedStack,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    Tags,
)
from constructs import Construct

class AutoScalingGroupStack(NestedStack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        vpc: ec2.Vpc,
        project_name: str,
        env_name: str,
        instance_type: str = "t3.micro",
        machine_image: ec2.IMachineImage = None,
        desired_capacity: int = 1,
        min_capacity: int = 1,
        max_capacity: int = 2,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        # Use default Amazon Linux 2 image if none provided
        ami = machine_image or ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE,
        )

        self.asg = autoscaling.AutoScalingGroup(
            self,
            "AutoScalingGroup",
            vpc=vpc,
            instance_type=ec2.InstanceType(instance_type),
            machine_image=ami,
            desired_capacity=desired_capacity,
            min_capacity=min_capacity,
            max_capacity=max_capacity,
            associate_public_ip_address=True,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )

        Tags.of(self.asg).add("Project", project_name)
        Tags.of(self.asg).add("Environment", env_name)
