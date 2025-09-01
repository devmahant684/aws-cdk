from aws_cdk import (
    NestedStack,
    aws_ecr as ecr,
    RemovalPolicy,
    Tags
)
from constructs import Construct

class EcrStack(NestedStack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        project_name: str,
        env_name: str,
        **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        repo_name = f"{project_name.lower()}-{env_name.lower()}-repository"

        # Create ECR repository
        self.repository = ecr.Repository(
            self,
            "ECRRepository",
            repository_name=repo_name,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_images=True,
        )

        # Add tags
        Tags.of(self.repository).add("Name", repo_name)
        Tags.of(self.repository).add("Project", project_name)
        Tags.of(self.repository).add("Environment", env_name)
