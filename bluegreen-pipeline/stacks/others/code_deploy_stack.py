from aws_cdk import (
    NestedStack,
    aws_codedeploy as codedeploy,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
)
from constructs import Construct


class DeployStack(NestedStack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        ecs_cluster: ecs.ICluster,
        ecs_service_name: str,
        blue_target_group: elbv2.IApplicationTargetGroup,
        green_target_group: elbv2.IApplicationTargetGroup,
        listener: elbv2.ApplicationListener,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        # Import the existing ECS service by attributes
        ecs_service = ecs.FargateService.from_fargate_service_attributes(
            self,
            "ImportedService",
            cluster=ecs_cluster,
            service_name=ecs_service_name,
        )

        # Define the CodeDeploy ECS Blue/Green deployment group
        self.deployment_group = codedeploy.EcsDeploymentGroup(
            self,
            "EcsDeploymentGroup",
            service=ecs_service,
            blue_green_deployment_config=codedeploy.EcsBlueGreenDeploymentConfig(
                blue_target_group=blue_target_group,
                green_target_group=green_target_group,
                listener=listener,
                termination_wait_time_in_minutes=60,
            ),
            auto_rollback=codedeploy.AutoRollbackConfig(
                failed_deployment=True,
                stopped_deployment=True,
            ),
        )
