import aws_cdk as core
import aws_cdk.assertions as assertions

from blue_green_infra.blue_green_infra_stack import BlueGreenInfraStack

# example tests. To run these tests, uncomment this file along with the example
# resource in blue_green_infra/blue_green_infra_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = BlueGreenInfraStack(app, "blue-green-infra")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
