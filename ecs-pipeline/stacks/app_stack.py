# from aws_cdk import Stack, Environment
# from constructs import Construct
# from stacks.ecs.ecs_stack import ECSASGStack
# from stacks.codebuild.codebuild_stack import PipelineWithASGStack


# class AppStack(Stack):
#     def __init__(self, scope: Construct, id: str, *, config: dict, env_name: str, base_stack, **kwargs):
#         super().__init__(scope, id, **kwargs)

        # # ECS Fargate service using BaseStack resources
        # self.ecs_stack = ECSFargateSimpleStack(
        #     self,
        #     "ECSFargateSimpleStack",
        #     vpc=base_stack.vpc,
        #     target_group=base_stack.target_group,
        #     repository=base_stack.repository,
        #     project_name=config["PROJECT_NAME"],
        #     env_name=env_name,
        #     desired_count=1,
        # )

        # # CodeBuild and CodePipeline stack integrated with the ECS service
        # self.pipeline_stack = PipelineWithBuildStack(
        #     self,
        #     "PipelineWithBuildStack",
        #     project_name=config["PROJECT_NAME"],
        #     env_name=env_name,
        #     connection_arn=config["CONNECTION_ARN"],
        #     repo_owner=config["REPO_OWNER"],
        #     repo_name=config["REPO_NAME"],
        #     branch_name=config["BRANCH_NAME"],
        #     ecs_service=self.ecs_stack.service,  # Pass the ECS Fargate service for deploy action
        # )




     

        # # Expose ECS service and cluster for external use
        # self.ecs_service = self.ecs_stack.service
        # self.cluster = self.ecs_stack.cluster
        # self.pipeline = self.pipeline_stack.pipeline

from aws_cdk import Stack, Environment, aws_ec2 as ec2
from constructs import Construct
from stacks.ecs.ecs_stack import ECSASGStack  # Renamed or your new ECS ASG stack
from stacks.codebuild.codebuild_stack import PipelineWithASGStack  # Pipeline stack for ASG ECS


class AppStack(Stack):
    def __init__(self, scope: Construct, id: str, *, config: dict, env_name: str, base_stack, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Define instance type explicitly as t2.micro
        instance_type_obj = ec2.InstanceType("t2.micro")

        # Instantiate the ECS ASG stack using base stack resources
        self.ecs_stack = ECSASGStack(
            self,
            "ECSASGStack",
            vpc=base_stack.vpc,
            target_group=base_stack.target_group,
            repository=base_stack.repository,
            project_name=config["PROJECT_NAME"],
            env_name=env_name,
            desired_count=2,
            instance_type=instance_type_obj,
        )

        # Instantiate the pipeline stack connected to ECS service
        self.pipeline_stack = PipelineWithASGStack(
            self,
            "PipelineWithASGStack",
            project_name=config["PROJECT_NAME"],
            env_name=env_name,
            connection_arn=config["CONNECTION_ARN"],
            repo_owner=config["REPO_OWNER"],
            repo_name=config["REPO_NAME"],
            branch_name=config["BRANCH_NAME"],
            ecs_service=self.ecs_stack.service,
            repository=base_stack.repository,
        )

        # Expose commonly used resources for external usage or integration
        self.ecs_service = self.ecs_stack.service
        self.cluster = self.ecs_stack.cluster
        self.pipeline = self.pipeline_stack.pipeline
