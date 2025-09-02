from aws_cdk import Stack, Environment
from constructs import Construct
# from stacks.ecs.ecs_stack import ECSFargateSimpleStack
# from stacks.codebuild.codebuild_stack import PipelineWithBuildStack
from stacks.ec2.autoscallinggroup_stack import AutoScalingGroupStack
from stacks.codebuild.codebuild_stack import PipelineWithASGStack

class AppStack(Stack):
    def __init__(self, scope: Construct, id: str, *, config: dict, env_name: str, base_stack, **kwargs):
        super().__init__(scope, id, **kwargs)

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




        # ASG stack using base_stack's VPC
        self.asg_stack = AutoScalingGroupStack(
            self,
            "AutoScalingGroupStack",
            vpc=base_stack.vpc,
            project_name=config["PROJECT_NAME"],
            env_name=env_name,
            instance_type="t3.micro",
            desired_capacity=1,
            min_capacity=1,
            max_capacity=2,
        )


         # Code pipeline integrated with the ASG stack
        self.pipeline_stack = PipelineWithASGStack(
            self,
            "PipelineWithASGStack",
            project_name=config["PROJECT_NAME"],
            env_name=env_name,
            connection_arn=config["CONNECTION_ARN"],
            repo_owner=config["REPO_OWNER"],
            repo_name=config["REPO_NAME"],
            branch_name=config["BRANCH_NAME"],
            asg_group=self.asg_stack.asg,
        )

        # # Expose ECS service and cluster for external use
        # self.ecs_service = self.ecs_stack.service
        # self.cluster = self.ecs_stack.cluster
        # self.pipeline = self.pipeline_stack.pipeline



          # Expose ASG and pipeline for external use
        self.asg = self.asg_stack.asg
        self.pipeline = self.pipeline_stack.pipeline
