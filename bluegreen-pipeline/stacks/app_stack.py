from aws_cdk import Stack
from constructs import Construct
from stacks.base_stack import BaseStack
from stacks.ecs.ecs_fargate_stack import ECSFargateBlueGreenStack
from stacks.codebuild.codepipeline_with_build_stack import PipelineWithBuildStack
from stacks.codebuild.codedeploy_stack import DeployStack


class AppStack(Stack):
    def __init__(self, scope: Construct, id: str, config: dict, env_name: str, *, base_stack: BaseStack, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Access shared resources from base_stack
        vpc = base_stack.vpc
        listener = base_stack.listener
        blue_tg = base_stack.blue_target_group
        green_tg = base_stack.green_target_group
        repository = base_stack.repository

        # Now pass these to nested stacks as needed
        self.ecs_stack = ECSFargateBlueGreenStack(
            self,
            "ECSStack",
            vpc=vpc,
            blue_tg=blue_tg,
            green_tg=green_tg,
            repository=repository,
            project_name=config["PROJECT_NAME"],
            env_name=env_name,
        )

        self.pipeline_stack = PipelineWithBuildStack(
            self,
            "PipelineStack",
            project_name=config["PROJECT_NAME"],
            env_name=env_name,
            connection_arn=config["CONNECTION_ARN"],
            repo_owner=config["REPO_OWNER"],
            repo_name=config["REPO_NAME"],
            branch_name=config["BRANCH_NAME"],
        )

        self.deploy_stack = DeployStack(
            self,
            "DeployStack",
            project_name=config["PROJECT_NAME"],
            env_name=env_name,
            ecs_cluster=self.ecs_stack.cluster,
            ecs_service_name=self.ecs_stack.ecs_service.service_name,
            blue_target_group=blue_tg,
            green_target_group=green_tg,
            listener=listener,
        )

        self.pipeline_stack.add_deploy_stage(self.deploy_stack.deployment_group)

        # Optionally export for higher-level references
        self.ecs_service = self.ecs_stack.ecs_service
        self.codepipeline = self.pipeline_stack.pipeline
        self.codebuild_project = self.pipeline_stack.build_project
        self.codedeploy_group = self.deploy_stack.deployment_group
