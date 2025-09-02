# from aws_cdk import (
#     aws_ecs as ecs,
#     aws_ec2 as ec2,
#     aws_iam as iam,
#     aws_logs as logs,
#     aws_ecr as ecr,
#     NestedStack,
#     aws_elasticloadbalancingv2 as elbv2,
#     Tags,
# )
# from constructs import Construct

# class ECSFargateSimpleStack(NestedStack):
#     def __init__(
#         self,
#         scope: Construct,
#         id: str,
#         *,
#         vpc: ec2.Vpc,
#         target_group: elbv2.ApplicationTargetGroup,
#         repository: ecr.Repository,
#         project_name: str,
#         env_name: str,
#         desired_count: int = 1,
#         **kwargs,
#     ) -> None:
#         super().__init__(scope, id, **kwargs)

#         # ECS Security Group
#         ecs_sg = ec2.SecurityGroup(
#             self,
#             "ECSSecurityGroup",
#             vpc=vpc,
#             description="Security group for ECS Fargate service",
#             allow_all_outbound=True,
#         )
#         ecs_sg.add_ingress_rule(
#             peer=ec2.Peer.any_ipv4(),
#             connection=ec2.Port.tcp(80),
#             description="Allow HTTP traffic to ECS tasks",
#         )

#         cluster_name = f"{project_name}-{env_name}-cluster"
#         execution_role_name = f"{project_name}-{env_name}-ecs-execution-role"
#         task_role_name = f"{project_name}-{env_name}-ecs-task-role"

#         # Create ECS Cluster (do NOT import)
#         cluster = ecs.Cluster(
#             self,
#             "ECSCluster",
#             vpc=vpc,
#             cluster_name=cluster_name,
#         )

#         # Create IAM Roles (do NOT import)
#         execution_role = iam.Role(
#             self,
#             "ECSExecutionRole",
#             role_name=execution_role_name,
#             assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
#             managed_policies=[
#                 iam.ManagedPolicy.from_aws_managed_policy_name(
#                     "service-role/AmazonECSTaskExecutionRolePolicy"
#                 )
#             ],
#         )

#         task_role = iam.Role(
#             self,
#             "ECSTaskRole",
#             role_name=task_role_name,
#             assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
#         )
#         task_role.add_managed_policy(
#             iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly")
#         )

#         # Task Definition
#         task_def = ecs.FargateTaskDefinition(
#             self,
#             "TaskDefinition",
#             family=f"{project_name}-{env_name}-taskdef",
#             memory_limit_mib=512,
#             cpu=256,
#             execution_role=execution_role,
#             task_role=task_role,
#         )

#         container_name = "my-container"
#         stream_prefix = f"{project_name.lower()}-logs"

#         container = task_def.add_container(
#             container_name,
#             image=ecs.ContainerImage.from_ecr_repository(repository, tag="latest"),
#             port_mappings=[ecs.PortMapping(container_port=80)],
#             logging=ecs.LogDrivers.aws_logs(
#                 stream_prefix=stream_prefix,
#                 log_retention=logs.RetentionDays.ONE_WEEK,
#             ),
#         )

#         # Create Fargate Service
#         fargate_service = ecs.FargateService(
#             self,
#             "FargateService",
#             cluster=cluster,
#             service_name=f"{project_name}-{env_name}-service",
#             task_definition=task_def,
#             desired_count=desired_count,
#             security_groups=[ecs_sg],
#             assign_public_ip=True,
#             vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
#         )

#         # Attach service to ALB target group
#         target_group.add_target(fargate_service)

#         # Tags
#         Tags.of(fargate_service).add("Name", f"{project_name}-{env_name}-ecs-service")
#         Tags.of(fargate_service).add("Environment", env_name)
#         Tags.of(fargate_service).add("Project", project_name)

#         # Exports
#         self.cluster = cluster
#         self.service = fargate_service
#         self.security_group = ecs_sg
#         self.execution_role = execution_role



from aws_cdk import (
    NestedStack,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_logs as logs,
    aws_ecr as ecr,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2,
    Tags,
    Duration,
)
from constructs import Construct


class ECSASGStack(NestedStack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        vpc: ec2.Vpc,
        target_group: elbv2.ApplicationTargetGroup,
        repository: ecr.Repository,
        project_name: str,
        env_name: str,
        desired_count: int = 1,
        instance_type: ec2.InstanceType = ec2.InstanceType("t3.micro"),
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # ECS Cluster
        cluster_name = f"{project_name}-{env_name}-cluster"
        cluster = ecs.Cluster(self, "ECSCluster", vpc=vpc, cluster_name=cluster_name)

        ecs_ami = ecs.EcsOptimizedImage.amazon_linux2()

        # Add capacity to cluster (creates AutoScalingGroup)
        asg = cluster.add_capacity(
            "EcsCapacity",
            instance_type=instance_type,
            desired_capacity=desired_count,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            machine_image=ecs_ami,
            associate_public_ip_address=True,
        )

        # IAM Roles for ECS Task
        execution_role = iam.Role(
            self,
            "ECSExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                )
            ],
            role_name=f"{project_name}-{env_name}-ecs-execution-role",
        )

        task_role = iam.Role(
            self,
            "ECSTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            role_name=f"{project_name}-{env_name}-ecs-task-role",
        )
        task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonEC2ContainerRegistryReadOnly"
            )
        )

        # EC2 Task Definition
        task_def = ecs.Ec2TaskDefinition(
            self,
            "TaskDefinition",
            family=f"{project_name}-{env_name}-taskdef",
            execution_role=execution_role,
            task_role=task_role,
        )

        container_name = "my-container"
        stream_prefix = f"{project_name.lower()}-logs"

        container = task_def.add_container(
            container_name,
            image=ecs.ContainerImage.from_ecr_repository(repository, tag="latest"),
            memory_reservation_mib=512,
            cpu=256,
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix=stream_prefix,
                log_retention=logs.RetentionDays.ONE_WEEK,
            ),
        )

        container.add_port_mappings(ecs.PortMapping(container_port=80))

        # EC2 Service
        service = ecs.Ec2Service(
            self,
            "EcsService",
            cluster=cluster,
            service_name=f"{project_name}-{env_name}-service",
            task_definition=task_def,
            desired_count=desired_count,
            health_check_grace_period=Duration.seconds(60),
        )

        target_group.add_target(service)

        Tags.of(service).add("Name", f"{project_name}-{env_name}-ecs-service")
        Tags.of(service).add("Environment", env_name)
        Tags.of(service).add("Project", project_name)

        self.cluster = cluster
        self.service = service
        self.auto_scaling_group = asg
        self.execution_role = execution_role
