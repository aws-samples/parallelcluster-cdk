# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import Stack, aws_ec2 as ec2


class HpcKeypairStack(Stack):
    def __init__(self, scope: Construct, id: str, config: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.admin_key_pair = ec2.CfnKeyPair(
            self,
            "ClusterKeyPair",
            key_name=config["key_name"],
            public_key_material=config["key_material"],
        )

        self.breakglass_key_pair = ec2.CfnKeyPair(
            self, "BreakGlassKeyPair", key_name="BreakGlass"
        )
