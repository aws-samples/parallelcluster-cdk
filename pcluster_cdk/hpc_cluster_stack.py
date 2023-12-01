# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import Stack, CustomResource, RemovalPolicy


class HpcClusterStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        cluster_provider,
        vpc,
        efs_id,
        efs_sg,
        lustre_id,
        lustre_sg,
        zfs_id,
        zfs_sg,
        config: dict,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        pcluster_controller_subnet = vpc.public_subnets[0].subnet_id
        # We use all 3 AZs for compute, so can just list in order
        pcluster_compute_subnet_1 = vpc.private_subnets[0].subnet_id
        pcluster_compute_subnet_2 = vpc.private_subnets[1].subnet_id
        pcluster_compute_subnet_3 = vpc.private_subnets[2].subnet_id

        self.additional_security_groups = [efs_sg, lustre_sg, zfs_sg]

        self.slurm_settings = {
            "QueueUpdateStrategy": "DRAIN",
            "ScaledownIdletime": "5",
            "CustomSlurmSettings": [
                {"JobRequeue": "0"},
            ],
        }

        self.ebs_settings = {
            "Encrypted": "true",
            "VolumeType": "gp3",
        }

        self.compute_settings = {
            "LocalStorage": {"RootVolume": dict({"Size": "200"}, **self.ebs_settings)}
        }

        self.iam_settings = {
            "AdditionalIamPolicies": [
                {"Policy": "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"},
            ]
        }

        self.compute_resource_networking_settings = {
            "PlacementGroup": {"Enabled": "true"}
        }

        self.common_compute_settings = {
            "MinCount": "0",
            "DisableSimultaneousMultithreading": "true",
            "Efa": {"Enabled": "true"},
            "Networking": self.compute_resource_networking_settings,
        }

        self.c6i_settings = {
            "Name": "c6i",
            "InstanceType": "c6i.32xlarge",
            **self.common_compute_settings,
        }

        self.c7i_settings = {
            "Name": "c7i",
            "InstanceType": "c7i.48xlarge",
            **self.common_compute_settings,
        }

        self.cluster_config = {
            "Image": {"Os": "alinux2"},
            "HeadNode": {
                "InstanceType": "m7i-flex.large",
                "LocalStorage": {
                    "RootVolume": dict({"Size": "100"}, **self.ebs_settings)
                },
                "Networking": {
                    "SubnetId": pcluster_controller_subnet,
                    "AdditionalSecurityGroups": self.additional_security_groups,
                },
                "Ssh": {
                    "KeyName": config["key_name"],
                    "AllowedIps": config["trusted_cidr"],
                },
                "Iam": self.iam_settings,
            },
            "Scheduling": {
                "Scheduler": "slurm",
                "SlurmSettings": self.slurm_settings,
                "SlurmQueues": [
                    {
                        "Name": "icl1",
                        "CapacityType": "ONDEMAND",
                        "JobExclusiveAllocation": "true",
                        "ComputeSettings": self.compute_settings,
                        "ComputeResources": [
                            dict({"MaxCount": "20"}, **self.c6i_settings)
                        ],
                        "Networking": {
                            "SubnetIds": [pcluster_compute_subnet_1],
                            "AdditionalSecurityGroups": self.additional_security_groups,
                        },
                        # "CustomActions": {
                        #     "OnNodeConfigured": self.compute_postinstall_sequence
                        # }
                    },
                    {
                        "Name": "icl2",
                        "CapacityType": "ONDEMAND",
                        "JobExclusiveAllocation": "true",
                        "ComputeSettings": self.compute_settings,
                        "ComputeResources": [
                            dict({"MaxCount": "20"}, **self.c6i_settings)
                        ],
                        "Networking": {
                            "SubnetIds": [pcluster_compute_subnet_2],
                            "AdditionalSecurityGroups": self.additional_security_groups,
                        },
                        # "CustomActions": {
                        #     "OnNodeConfigured": self.compute_postinstall_sequence
                        # }
                    },
                    {
                        "Name": "icl3",
                        "CapacityType": "ONDEMAND",
                        "JobExclusiveAllocation": "true",
                        "ComputeSettings": self.compute_settings,
                        "ComputeResources": [
                            dict({"MaxCount": "20"}, **self.c6i_settings)
                        ],
                        "Networking": {
                            "SubnetIds": [pcluster_compute_subnet_3],
                            "AdditionalSecurityGroups": self.additional_security_groups,
                        },
                        # "CustomActions": {
                        #     "OnNodeConfigured": self.compute_postinstall_sequence
                        # }
                    },
                    {
                        "Name": "spr1",
                        "CapacityType": "ONDEMAND",
                        "JobExclusiveAllocation": "true",
                        "ComputeSettings": self.compute_settings,
                        "ComputeResources": [
                            dict({"MaxCount": "20"}, **self.c7i_settings)
                        ],
                        "Networking": {
                            "SubnetIds": [pcluster_compute_subnet_1],
                            "AdditionalSecurityGroups": self.additional_security_groups,
                        },
                        # "CustomActions": {
                        #     "OnNodeConfigured": self.compute_postinstall_sequence
                        # }
                    },
                    {
                        "Name": "spr2",
                        "CapacityType": "ONDEMAND",
                        "JobExclusiveAllocation": "true",
                        "ComputeSettings": self.compute_settings,
                        "ComputeResources": [
                            dict({"MaxCount": "20"}, **self.c7i_settings)
                        ],
                        "Networking": {
                            "SubnetIds": [pcluster_compute_subnet_2],
                            "AdditionalSecurityGroups": self.additional_security_groups,
                        },
                        # "CustomActions": {
                        #     "OnNodeConfigured": self.compute_postinstall_sequence
                        # }
                    },
                    {
                        "Name": "spr3",
                        "CapacityType": "ONDEMAND",
                        "JobExclusiveAllocation": "true",
                        "ComputeSettings": self.compute_settings,
                        "ComputeResources": [
                            dict({"MaxCount": "20"}, **self.c7i_settings)
                        ],
                        "Networking": {
                            "SubnetIds": [pcluster_compute_subnet_3],
                            "AdditionalSecurityGroups": self.additional_security_groups,
                        },
                        # "CustomActions": {
                        #     "OnNodeConfigured": self.compute_postinstall_sequence
                        # }
                    },
                ],
            },
            "SharedStorage": [
                {
                    "Name": "EfsFromCDK",
                    "StorageType": "Efs",
                    "MountDir": "/efs",
                    "EfsSettings": {"FileSystemId": efs_id},
                },
                {
                    "Name": "LustreFromCDK",
                    "StorageType": "FsxLustre",
                    "MountDir": "/lustre",
                    "FsxLustreSettings": {"FileSystemId": lustre_id},
                },
                {
                    "Name": "ZfsFromCDK",
                    "StorageType": "FsxOpenZfs",
                    "MountDir": "/zfs",
                    "FsxOpenZfsSettings": {"VolumeId": zfs_id},
                },
            ],
        }

        self.pcluster = CustomResource(
            self,
            "HPC_CLUSTER",
            resource_type="Custom::PClusterCluster",
            removal_policy=RemovalPolicy.RETAIN,
            service_token=cluster_provider.get_att("Outputs.ServiceToken").to_string(),
            pascal_case_properties=True,
            properties={
                "ClusterName": config["label"],
                "ClusterConfiguration": self.cluster_config,
                # "RollbackOnFailure": config["pcluster"]["rollback_on_failure"],
            },
        )
