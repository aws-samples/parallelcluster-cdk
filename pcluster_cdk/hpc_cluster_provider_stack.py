# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import Stack, aws_cloudformation as cfn


class HpcClusterProviderStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: dict,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env = kwargs.get("env")
        region = env.region

        pcluster_version = config["pcluster"]["version"]

        self.cluster_provider = cfn.CfnStack(
            self,
            "HPC_CLUSTER_PROVIDER",
            template_url=f"https://{region}-aws-parallelcluster.s3.{region}.amazonaws.com/parallelcluster/{pcluster_version}/templates/custom_resource/cluster.yaml",
            timeout_in_minutes=30,
        )
