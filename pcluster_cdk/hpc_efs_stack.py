# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_efs as efs,
    aws_ssm as ssm,
    CfnOutput,
    RemovalPolicy,
)


class HpcEfsStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc, config: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.hpcefs_sg = ec2.SecurityGroup(
            self,
            "HPC_SG_EFS",
            vpc=vpc,
            allow_all_outbound=True,
        )

        self.hpcefs_sg.add_ingress_rule(
            self.hpcefs_sg, ec2.Port.tcp(2049), "Allow NFS connection to EFS"
        )

        self.hpcefs = efs.FileSystem(
            self,
            "HPC_EFS",
            vpc=vpc,
            security_group=self.hpcefs_sg,
            enable_automatic_backups=True,
            encrypted=True,
            performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,
            removal_policy=RemovalPolicy.DESTROY,
        )

        CfnOutput(self, "EFSFileSystemId", value=self.hpcefs.file_system_id)

        ssm.StringParameter(
            self,
            "HPC_EFS_DNS_NAME_PARAMETER",
            parameter_name=config["parameter_root"] + "/efs_dns_name",
            string_value=f"{self.hpcefs.file_system_id}.efs.{self.region}.amazonaws.com",
        )
