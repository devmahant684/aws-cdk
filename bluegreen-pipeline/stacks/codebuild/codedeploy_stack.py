from aws_cdk import (
    NestedStack,
    Duration,
    aws_codedeploy as codedeploy,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
)
from constructs import Construct
from aws_cdk import Duration


class DeployStack(NestedStack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        project_name: str,           # explicitly declared parameter
        env_name: str,     
        ecs_cluster: ecs.ICluster,
        ecs_service_name: str,
        blue_target_group: elbv2.IApplicationTargetGroup,
        green_target_group: elbv2.IApplicationTargetGroup,
        listener: elbv2.ApplicationListener,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

         # Create named CodeDeploy application
        self.codedeploy_app = codedeploy.EcsApplication(
            self,
            "CodeDeployApplication",
            application_name=f"{project_name}-{env_name}-codedeploy-app",
        )

        self.deployment_group = codedeploy.EcsDeploymentGroup(
            self,
            "EcsDeploymentGroup",
            application=self.codedeploy_app,
            deployment_group_name=f"{project_name}-{env_name}-deployment-group",
            service=ecs.FargateService.from_fargate_service_attributes(
                self,
                "ImportedService",
                cluster=ecs_cluster,
                service_name=ecs_service_name,
            ),
            blue_green_deployment_config=codedeploy.EcsBlueGreenDeploymentConfig(
                blue_target_group=blue_target_group,
                green_target_group=green_target_group,
                listener=listener,
                termination_wait_time=Duration.minutes(5),
            ),
            auto_rollback=codedeploy.AutoRollbackConfig(
                failed_deployment=True, stopped_deployment=True
            ),
        )
