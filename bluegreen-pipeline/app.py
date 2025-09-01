#!/usr/bin/env python3
from aws_cdk import App, Environment
from utils.config import get_config
from stacks.base_stack import BaseStack      # Example: if you named base stack so
from stacks.app_stack import AppStack

def main():
    app = App()                # Now App will be recognized
    config = get_config()
    env_name = config["ENV"]
    cdk_env = Environment(account=config["ACCOUNT"], region=config["REGION"])

    base_stack = BaseStack(
        app,
        f"{config['PROJECT_NAME']}-{env_name}-BaseStack",
        config=config,
        env_name=env_name,
        env=cdk_env,
    )

    app_stack = AppStack(
        app,
        f"{config['PROJECT_NAME']}-{env_name}-AppStack",
        config=config,
        env_name=env_name,
        env=cdk_env,
        base_stack=base_stack,
    )

    app_stack.add_dependency(base_stack)

    app.synth()

if __name__ == "__main__":
    main()
