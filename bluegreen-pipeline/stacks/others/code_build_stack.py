from aws_cdk import (
    NestedStack,
    Stack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cp_actions,
    aws_codebuild as codebuild,
    aws_codedeploy as codedeploy,
    aws_iam as iam,
    aws_elasticloadbalancingv2 as elbv2,
    aws_ecs as ecs,
    Tags,
)
from aws_cdk.aws_codepipeline import ArtifactPath
from constructs import Construct


class PipelineStack(NestedStack):
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
        ecr_repository_uri: str,
        ecs_cluster: ecs.ICluster,
        ecs_service_name: str,
        blue_target_group: elbv2.IApplicationTargetGroup,
        green_target_group: elbv2.IApplicationTargetGroup,
        ecs_task_execution_role_name: str,
        listener: elbv2.ApplicationListener,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        pipeline_name = f"{project_name}-{env_name}-pipeline"

        region = Stack.of(self).region
        account = Stack.of(self).account

        # Extract repository name from URI (assumes format: <account>.dkr.ecr.<region>.amazonaws.com/<repo-name>)
        repo_name_from_uri = ecr_repository_uri.split('/')[-1]

        # Artifacts
        source_output = codepipeline.Artifact()
        build_output = codepipeline.Artifact()

        # Create pipeline
        pipeline = codepipeline.Pipeline(self, "Pipeline", pipeline_name=pipeline_name)

        # Source: CodeStar Connections (GitHub)
        source_action = cp_actions.CodeStarConnectionsSourceAction(
            action_name="GitHub_Source",
            connection_arn=connection_arn,
            owner=repo_owner,
            repo=repo_name,
            branch=branch_name,
            output=source_output,
            trigger_on_push=True,
        )
        pipeline.add_stage(stage_name="Source", actions=[source_action])

        # Build: CodeBuild project
        build_project = codebuild.PipelineProject(
            self,
            "BuildProject",
            project_name=f"{project_name}-{env_name}-codebuild",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                privileged=True,
            ),
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yaml"),
            environment_variables={
                "REPOSITORY_URI": codebuild.BuildEnvironmentVariable(value=ecr_repository_uri),
            },
        )

        build_project.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:CompleteLayerUpload",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "ecr:InitiateLayerUpload",
                    "ecr:PutImage",
                    "ecr:UploadLayerPart",
                    "ecr:DescribeImages",
                    "ecr:ListImages",
                    "ecs:DescribeTaskDefinition",
                    "ecs:RegisterTaskDefinition",
                    "ecs:UpdateService",
                    "ecs:DescribeServices",
                    "iam:PassRole",
                ],
                resources=[
                    "*",  # for actions that require wildcard
                    f"arn:aws:iam::{account}:role/{ecs_task_execution_role_name}",
                ],
            )
        )




        build_action = cp_actions.CodeBuildAction(
            action_name="CodeBuild",
            project=build_project,
            input=source_output,
            outputs=[build_output],
        )
        pipeline.add_stage(stage_name="Build", actions=[build_action])

        # Deploy: CodeDeploy ECS Blue/Green
        deployment_group = codedeploy.EcsDeploymentGroup(
            self,
            "EcsDeploymentGroup",
            service=ecs.FargateService.from_fargate_service_attributes(
                self,
                "ImportedService",
                service_name=ecs_service_name,
                cluster=ecs_cluster,
            ),
            blue_green_deployment_config=codedeploy.EcsBlueGreenDeploymentConfig(
                blue_target_group=blue_target_group,
                green_target_group=green_target_group,
                listener=listener,
                termination_wait_time_in_minutes=60,
            ),
        #    load_balancer=codedeploy.LoadBalancer(
        #         target_group=blue_target_group,
        #         green_target_group=green_target_group,
        #     ),
            auto_rollback=codedeploy.AutoRollbackConfig(
                failed_deployment=True,
                stopped_deployment=True,
            ),
        )

        deploy_action = cp_actions.CodeDeployEcsDeployAction(
            action_name="ECS_BlueGreen_Deploy",
            deployment_group=deployment_group,
            task_definition_template_file=ArtifactPath(build_output, "taskdef.json"),
            app_spec_template_file=ArtifactPath(build_output, "appspec.yaml"),
        )
        pipeline.add_stage(stage_name="Deploy", actions=[deploy_action])

        Tags
        Tags.of(pipeline).add("Name", pipeline_name)
        Tags.of(pipeline).add("Environment", env_name)
        Tags.of(pipeline).add("Project", project_name)
