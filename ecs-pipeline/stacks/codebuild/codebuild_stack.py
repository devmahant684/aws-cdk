# from aws_cdk import (
#     NestedStack,
#     aws_codepipeline as codepipeline,
#     aws_codepipeline_actions as cp_actions,
#     aws_codebuild as codebuild,
#     aws_iam as iam,
# )
# from constructs import Construct


# class PipelineWithBuildStack(NestedStack):
#     def __init__(
#         self,
#         scope: Construct,
#         id: str,
#         *,
#         project_name: str,
#         env_name: str,
#         connection_arn: str,
#         repo_owner: str,
#         repo_name: str,
#         branch_name: str,
#         ecs_service,     
#         **kwargs,
#     ):
#         super().__init__(scope, id, **kwargs)

#         # IAM Role for CodePipeline
#         pipeline_role = iam.Role(
#             self,
#             "CodePipelineRole",
#             role_name=f"{project_name}-{env_name}-codepipeline-role",
#             assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com"),
#         )

#         # IAM Role for CodeBuild with needed permissions
#         build_role = iam.Role(
#             self,
#             "CodeBuildRole",
#             role_name=f"{project_name}-{env_name}-codebuild-role",
#             assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
#         )
#         build_role.add_to_policy(
#             iam.PolicyStatement(
#                 actions=[
#                     "s3:GetObject",
#                     "ecr:GetAuthorizationToken",
#                     "ecr:BatchCheckLayerAvailability",
#                     "ecr:BatchGetImage",
#                     "ecr:PutImage",
#                     "ecr:InitiateLayerUpload",
#                     "ecr:UploadLayerPart",
#                     "ecr:CompleteLayerUpload",
#                     "ecs:DescribeServices",
#                     "ecs:DescribeTaskDefinition",
#                     "ecs:UpdateService",
#                     "iam:PassRole",
#                 ],
#                 resources=["*"],
#             )
#         )

#         # Pipeline definition
#         self.pipeline = codepipeline.Pipeline(
#             self,
#             "Pipeline",
#             pipeline_name=f"{project_name}-{env_name}-pipeline",
#             role=pipeline_role,
#         )

#         # Artifacts
#         self.source_output = codepipeline.Artifact(artifact_name="SourceArtifact")
#         self.build_output = codepipeline.Artifact(artifact_name="BuildArtifact")

#         # Source stage - GitHub via CodeStar connection
#         source_action = cp_actions.CodeStarConnectionsSourceAction(
#             action_name="GitHub_Source",
#             connection_arn=connection_arn,
#             owner=repo_owner,
#             repo=repo_name,
#             branch=branch_name,
#             output=self.source_output,
#             trigger_on_push=True,
#         )
#         self.pipeline.add_stage(stage_name="Source", actions=[source_action])

#         # Build project (buildspec should output imagedefinitions.json only)
#         self.build_project = codebuild.PipelineProject(
#             self,
#             "BuildProject",
#             project_name=f"{project_name}-{env_name}-codebuild",
#             build_spec=codebuild.BuildSpec.from_source_filename("ecs-pipeline/buildspec.yaml"),
#             environment=codebuild.BuildEnvironment(
#                 build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
#                 privileged=True,
#             ),
#             role=build_role,
#         )

#         # Build action
#         self.build_action = cp_actions.CodeBuildAction(
#             action_name="Build",
#             project=self.build_project,
#             input=self.source_output,
#             outputs=[self.build_output],
#         )
#         self.pipeline.add_stage(stage_name="Build", actions=[self.build_action])

#         # Deploy Stage using EcsDeployAction
#         deploy_action = cp_actions.EcsDeployAction(
#             action_name="Deploy",
#             service=ecs_service,
#             input=self.build_output,  # imagedefinitions.json
#         )
#         self.pipeline.add_stage(stage_name="Deploy", actions=[deploy_action])







from aws_cdk import (
    NestedStack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cp_actions,
    aws_codebuild as codebuild,
    aws_iam as iam,
)
from constructs import Construct

class PipelineWithASGStack(NestedStack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        project_name: str,
        env_name: str,
        asg_name: str,
        connection_arn: str,
        repo_owner: str,
        repo_name: str,
        branch_name: str,
        asg_group,  # AutoScalingGroup instance
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        pipeline_role = iam.Role(
            self,
            "CodePipelineRole",
            role_name=f"{project_name}-{env_name}-codepipeline-role",
            assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com"),
        )

        build_role = iam.Role(
            self,
            "CodeBuildRole",
            role_name=f"{project_name}-{env_name}-codebuild-role",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
        )
        build_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "autoscaling:UpdateAutoScalingGroup",
                    "autoscaling:CreateLaunchConfiguration",
                    "ec2:CreateImage",
                    "ec2:DescribeInstances",
                    "iam:PassRole",
                ],
                resources=["*"],
            )
        )

        self.pipeline = codepipeline.Pipeline(
            self,
            "Pipeline",
            pipeline_name=f"{project_name}-{env_name}-pipeline",
            role=pipeline_role,
        )

        self.source_output = codepipeline.Artifact(artifact_name="SourceArtifact")
        self.build_output = codepipeline.Artifact(artifact_name="BuildArtifact")

        # Source stage: GitHub repo via CodeStar connection
        source_action = cp_actions.CodeStarConnectionsSourceAction(
            action_name="GitHub_Source",
            connection_arn=connection_arn,
            owner=repo_owner,
            repo=repo_name,
            branch=branch_name,
            output=self.source_output,
            trigger_on_push=True,
        )
        self.pipeline.add_stage(stage_name="Source", actions=[source_action])

        # Build stage referencing ecs-pipeline/buildspec.yaml
        self.build_project = codebuild.PipelineProject(
            self,
            "BuildProject",
            project_name=f"{project_name}-{env_name}-codebuild",
            build_spec=codebuild.BuildSpec.from_source_filename("ecs-pipeline/buildspec.yaml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                privileged=False,
                environment_variables={
                    "PROJECT_NAME": codebuild.BuildEnvironmentVariable(value=project_name),
                    "ENV": codebuild.BuildEnvironmentVariable(value=env_name),
                    "ASG_NAME": codebuild.BuildEnvironmentVariable(value=asg_name),
                },
            ),
            role=build_role,
        )
        build_action = cp_actions.CodeBuildAction(
            action_name="Build",
            project=self.build_project,
            input=self.source_output,
            outputs=[self.build_output],
        )
        self.pipeline.add_stage(stage_name="Build", actions=[build_action])

        # Deploy stage referencing ecs-pipeline/buildspec-deploy.yaml
        self.deploy_project = codebuild.PipelineProject(
            self,
            "DeployProject",
            project_name=f"{project_name}-{env_name}-deploy",
            build_spec=codebuild.BuildSpec.from_source_filename("ecs-pipeline/buildspec-deploy.yaml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
            ),
            role=build_role,
        )
        deploy_action = cp_actions.CodeBuildAction(
            action_name="Deploy",
            project=self.deploy_project,
            input=self.build_output,
        )
        self.pipeline.add_stage(stage_name="Deploy", actions=[deploy_action])

