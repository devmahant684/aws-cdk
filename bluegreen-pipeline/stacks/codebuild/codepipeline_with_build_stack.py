from aws_cdk import (
    NestedStack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cp_actions,
    aws_codebuild as codebuild,
    aws_iam as iam,
)
from aws_cdk.aws_codepipeline import ArtifactPath
from constructs import Construct


class PipelineWithBuildStack(NestedStack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        project_name: str,
        env_name: str,
        connection_arn: str,
        repo_owner: str,
        repo_name: str,
        branch_name: str,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        # IAM Role for CodePipeline
        pipeline_role = iam.Role(
            self,
            "CodePipelineRole",
            role_name=f"{project_name}-{env_name}-codepipeline-role",
            assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com"),
        )

        # IAM Role for CodeBuild with needed permissions
        build_role = iam.Role(
            self,
            "CodeBuildRole",
            role_name=f"{project_name}-{env_name}-codebuild-role",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
        )
        build_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:GetObject",
                    "s3:GetObjectVersion",
                    "s3:GetBucketVersioning",
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:BatchGetImage",
                    "ecr:PutImage",
                    "ecr:InitiateLayerUpload",
                    "ecr:UploadLayerPart",
                    "ecr:CompleteLayerUpload",
                    "ecs:DescribeServices",
                    "ecs:RegisterTaskDefinition",
                    "ecs:UpdateService",
                    "ecs:DescribeTaskDefinition",
                    "iam:PassRole",
                    "codedeploy:*",
                ],
                resources=["*"],
            )
        )

        # Pipeline definition
        self.pipeline = codepipeline.Pipeline(
            self,
            "Pipeline",
            pipeline_name=f"{project_name}-{env_name}-pipeline",
            role=pipeline_role
        )

        # Artifacts
        self.source_output = codepipeline.Artifact(artifact_name="SourceArtifact")
        self.build_output = codepipeline.Artifact(artifact_name="BuildArtifact")

        # Source stage - GitHub via CodeStar connection
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

        # Build project
        self.build_project = codebuild.PipelineProject(
            self,
            "BuildProject",
            project_name=f"{project_name}-{env_name}-codebuild",
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yaml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                privileged=True,
            ),
            role=build_role
        )
       

        # Build action
        self.build_action = cp_actions.CodeBuildAction(
            action_name="Build",
            project=self.build_project,
            input=self.source_output,
            outputs=[self.build_output],
        )
        self.pipeline.add_stage(stage_name="Build", actions=[self.build_action])

    # Add deploy stage using ECS CodeDeploy Blue/Green deployment
    def add_deploy_stage(self, deployment_group):
        deploy_action = cp_actions.CodeDeployEcsDeployAction(
            action_name="Deploy",
            deployment_group=deployment_group,
            task_definition_template_input=self.build_output,
            app_spec_template_input=self.build_output,
        )
        self.pipeline.add_stage(stage_name="Deploy", actions=[deploy_action])
