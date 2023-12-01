# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import Stack, aws_ec2 as ec2, CfnOutput


class HpcNetworkStack(Stack):
    def __init__(self, scope: Construct, id: str, config: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        public_subnet = ec2.SubnetConfiguration(
            name="public", subnet_type=ec2.SubnetType.PUBLIC
        )
        private_subnet = ec2.SubnetConfiguration(
            name="private", subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
        )
        isolated_subnet = ec2.SubnetConfiguration(
            name="isolated", subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
        )

        if config["vpc"]["nat_per_az"]:
            gateways = config["vpc"]["enabled_az_count"]
        else:
            gateways = 1

        self.hpcvpc = ec2.Vpc(
            self,
            "HPC_VPC",
            ip_addresses=ec2.IpAddresses.cidr(
                cidr_block=config["vpc"]["cidr"],
            ),
            max_azs=config["vpc"]["enabled_az_count"],
            subnet_configuration=[public_subnet, private_subnet, isolated_subnet],
            nat_gateways=gateways,
        )

        for id, subnet in enumerate(self.hpcvpc.public_subnets):
            label = f"PUBLIC subnet {id}"
            CfnOutput(self, label, value=subnet.subnet_id)
        for id, subnet in enumerate(self.hpcvpc.private_subnets):
            label = f"PRIVATE subnet {id}"
            CfnOutput(self, label, value=subnet.subnet_id)
        for id, subnet in enumerate(self.hpcvpc.isolated_subnets):
            label = f"ISOLATED subnet {id}"
            CfnOutput(self, label, value=subnet.subnet_id)
