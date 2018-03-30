from pentagon.component import ComponentBase
import os


class AWSVpc(ComponentBase):

    _required_parameters = ['aws_region']
