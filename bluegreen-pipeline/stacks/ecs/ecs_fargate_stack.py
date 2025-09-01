from aws_cdk import (
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_logs as logs,
    aws_ecr as ecr,
    NestedStack,
    Tags
)
from constructs import Construct

class ECSFargateBlueGreenStack(NestedStack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        vpc: ec2.Vpc,
        blue_tg: elbv2.ApplicationTargetGroup,
        green_tg: elbv2.ApplicationTargetGroup,
        repository: ecr.Repository,  # ✅ NEW
        project_name: str,
        env_name: str,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        self.green_tg = green_tg

        # 🔐 ECS Security Group
        ecs_sg = ec2.SecurityGroup(
            self,
            "ECSSecurityGroup",
            vpc=vpc,
            description="Security group for ECS Fargate service",
            allow_all_outbound=True,
        )
        ecs_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP traffic to ECS tasks"
        )

        # 📦 ECS Cluster with custom name
        cluster = ecs.Cluster(
            self,
            "ECSCluster",
            vpc=vpc,
            cluster_name=f"{project_name}-{env_name}-cluster"
        )

        # 🧾 IAM Execution Role
        execution_role = iam.Role(
            self, "ECSExecutionRole",
            role_name=f"{project_name}-{env_name}-ecs-execution-role",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
            ]
        )

        # 🧾 IAM Task Role
        task_role = iam.Role(
            self, "ECSTaskRole",
            role_name=f"{project_name}-{env_name}-ecs-task-role",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly")
        )

        # 🧱 Task Definition
        task_def = ecs.FargateTaskDefinition(
            self, "TaskDef",
            family=f"{project_name}-{env_name}-taskdef",
            memory_limit_mib=512,
            cpu=256,
            execution_role=execution_role,
            task_role=task_role,
        )

        container_name = "my-container"
        stream_prefix = f"{project_name.lower()}-logs"

        # 🐳 Container Definition (no hardcoded URI)
        task_def.add_container(
            container_name,
            image=ecs.ContainerImage.from_ecr_repository(repository, tag="latest"),  # ✅ UPDATED
            port_mappings=[ecs.PortMapping(container_port=80)],
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix=stream_prefix,
                log_retention=logs.RetentionDays.ONE_WEEK
            )
        )

        # 🚀 ECS Fargate Service
        self.ecs_service = ecs.CfnService(
            self, "FargateService",
            service_name=f"{project_name}-{env_name}-service",
            cluster=cluster.cluster_arn,
            task_definition=task_def.task_definition_arn,
            launch_type="FARGATE",
            desired_count=1,
            network_configuration=ecs.CfnService.NetworkConfigurationProperty(
                awsvpc_configuration=ecs.CfnService.AwsVpcConfigurationProperty(
                    assign_public_ip="ENABLED",
                    subnets=[subnet.subnet_id for subnet in vpc.public_subnets],
                    security_groups=[ecs_sg.security_group_id]
                )
            ),
            deployment_controller=ecs.CfnService.DeploymentControllerProperty(
                type="CODE_DEPLOY"
            ),
            load_balancers=[
                ecs.CfnService.LoadBalancerProperty(
                    container_name=container_name,
                    container_port=80,
                    target_group_arn=blue_tg.target_group_arn
                )
            ]
        )

        # 🏷️ Tags
        Tags.of(self.ecs_service).add("Name", f"{project_name}-{env_name}-ecs-service")
        Tags.of(self.ecs_service).add("Environment", env_name)
        Tags.of(self.ecs_service).add("Project", project_name)

        # 🔁 Exports
        self.cluster = cluster
        self.service_name = self.ecs_service.ref
        self.security_group = ecs_sg
        self.execution_role = execution_role
