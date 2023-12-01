# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

#!/usr/bin/env python3
import os
import json
import aws_cdk as cdk

from pcluster_cdk.hpc_keypair_stack import HpcKeypairStack
from pcluster_cdk.hpc_network_stack import HpcNetworkStack
from pcluster_cdk.hpc_cluster_provider_stack import HpcClusterProviderStack
from pcluster_cdk.hpc_cluster_stack import HpcClusterStack
from pcluster_cdk.hpc_efs_stack import HpcEfsStack
from pcluster_cdk.hpc_lustre_stack import HpcLustreStack
from pcluster_cdk.hpc_zfs_stack import HpcZfsStack

from cdk_nag import AwsSolutionsChecks, NagSuppressions


default_config_file = "config"
app_config = os.getenv("CDK_APP_CONFIG", default_config_file)

app_config = os.environ["CDK_APP_CONFIG"]

with open(str(app_config + ".json"), "r") as config_json:
    global_config = json.load(config_json)

deploy_env = cdk.Environment(
    account=os.environ["CDK_DEPLOY_ACCOUNT"], region=os.environ["CDK_DEPLOY_REGION"]
)

app = cdk.App()

hpc_keypairs = HpcKeypairStack(
    app,
    "HpcKeypairs",
    config=global_config,
    env=deploy_env,
)

hpc_network = HpcNetworkStack(
    app,
    "HpcNetwork",
    config=global_config,
    env=deploy_env,
)

hpc_efs = HpcEfsStack(
    scope=app,
    id="HpcEfsStack",
    vpc=hpc_network.hpcvpc,
    config=global_config,
    env=deploy_env,
)

hpc_lustre = HpcLustreStack(
    scope=app,
    id="HpcLustreStack",
    vpc=hpc_network.hpcvpc,
    config=global_config,
    env=deploy_env,
)

hpc_zfs = HpcZfsStack(
    scope=app,
    id="HpcZfsStack",
    vpc=hpc_network.hpcvpc,
    config=global_config,
    env=deploy_env,
)

hpc_cluster_provider = HpcClusterProviderStack(
    app,
    "HpcClusterProvider",
    config=global_config,
    env=deploy_env,
)

hpc_cluster_stack = HpcClusterStack(
    app,
    "HpcCluster",
    cluster_provider=hpc_cluster_provider.cluster_provider,
    vpc=hpc_network.hpcvpc,
    efs_id=hpc_efs.hpcefs.file_system_id,
    efs_sg=hpc_efs.hpcefs_sg.security_group_id,
    lustre_id=hpc_lustre.hpclustre.file_system_id,
    lustre_sg=hpc_lustre.hpclustre_sg.security_group_id,
    zfs_id=hpc_zfs.hpczfs.attr_root_volume_id,
    zfs_sg=hpc_zfs.hpczfs_sg.security_group_id,
    config=global_config,
    env=deploy_env,
)

cdk.Aspects.of(app).add(AwsSolutionsChecks())

NagSuppressions.add_stack_suppressions(
    hpc_network,
    [
        {
            "id": "AwsSolutions-VPC7",
            "reason": "VPC flow logs not desirable for testing.",
        }
    ],
)

NagSuppressions.add_stack_suppressions(
    hpc_lustre,
    [
        {
            "id": "AwsSolutions-S1",
            "reason": "S3 server access logging not desirable for testing.",
        }
    ],
)

app.synth()
