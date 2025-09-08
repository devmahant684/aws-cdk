import os
from dotenv import load_dotenv


load_dotenv()


def get_config() -> dict:
    return {
        "PROJECT_NAME": os.getenv("PROJECT_NAME"),
        "ENV": os.getenv("ENV"),
        "REGION": os.getenv("REGION"),
        "ACCOUNT": os.getenv("ACCOUNT"),
        "VPC_CIDR": os.getenv("VPC_CIDR"),
        "NUM_PUBLIC_SUBNETS": int(os.getenv("NUM_PUBLIC_SUBNETS")),
        "NUM_PRIVATE_SUBNETS": int(os.getenv("NUM_PRIVATE_SUBNETS")),
        "CODESTAR_CONNECTION_ARN": os.getenv("CONNECTION_ARN"),
        "REPO_OWNER": os.getenv("REPO_OWNER"),
        "REPO_NAME": os.getenv("REPO_NAME"),
        "BRANCH_NAME": os.getenv("BRANCH_NAME", "main"),
    }

