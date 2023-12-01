# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_fsx as fsx,
    aws_ssm as ssm,
    CfnOutput,
)


class HpcZfsStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc, config: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        zfs_subnet = vpc.private_subnets[0]

        self.hpczfs_sg = ec2.SecurityGroup(
            self,
            "HPC_SG_ZFS",
            vpc=vpc,
            allow_all_outbound=True,
        )

        self.hpczfs_sg.add_ingress_rule(
            self.hpczfs_sg, ec2.Port.tcp(111), "Allow NFS connection to FSxZ"
        )
        self.hpczfs_sg.add_ingress_rule(
            self.hpczfs_sg, ec2.Port.udp(111), "Allow NFS connection to FSxZ"
        )
        self.hpczfs_sg.add_ingress_rule(
            self.hpczfs_sg, ec2.Port.tcp(2049), "Allow NFS connection to FSxZ"
        )
        self.hpczfs_sg.add_ingress_rule(
            self.hpczfs_sg, ec2.Port.udp(2049), "Allow NFS connection to FSxZ"
        )
        self.hpczfs_sg.add_ingress_rule(
            self.hpczfs_sg,
            ec2.Port.tcp_range(20001, 20003),
            "Allow NFS connection to FSxZ",
        )
        self.hpczfs_sg.add_ingress_rule(
            self.hpczfs_sg,
            ec2.Port.udp_range(20001, 20003),
            "Allow NFS connection to FSxZ",
        )

        zfs_config = fsx.CfnFileSystem.OpenZFSConfigurationProperty(
            deployment_type="SINGLE_AZ_2",
            automatic_backup_retention_days=7,
            copy_tags_to_backups=True,
            copy_tags_to_volumes=True,
            daily_automatic_backup_start_time="03:00",
            options=["DELETE_CHILD_VOLUMES_AND_SNAPSHOTS"],
            throughput_capacity=config["zfs"]["throughput"],
            weekly_maintenance_start_time="7:06:00",
            disk_iops_configuration=fsx.CfnFileSystem.DiskIopsConfigurationProperty(
                mode="AUTOMATIC"
            ),
            root_volume_configuration=fsx.CfnFileSystem.RootVolumeConfigurationProperty(
                copy_tags_to_snapshots=True,
                data_compression_type="ZSTD",
                nfs_exports=[
                    fsx.CfnFileSystem.NfsExportsProperty(
                        client_configurations=[
                            fsx.CfnFileSystem.ClientConfigurationsProperty(
                                clients=vpc.vpc_cidr_block,
                                options=["rw", "crossmnt", "async", "no_root_squash"],
                            )
                        ]
                    )
                ],
                read_only=False,
            ),
        )

        self.hpczfs = fsx.CfnFileSystem(
            self,
            "HPC_ZFS",
            file_system_type="OPENZFS",
            subnet_ids=[zfs_subnet.subnet_id],
            security_group_ids=[self.hpczfs_sg.security_group_id],
            storage_capacity=config["zfs"]["capacity"],
            storage_type="SSD",
            open_zfs_configuration=zfs_config,
        )

        CfnOutput(self, "ZFSSharedVolumeId", value=self.hpczfs.attr_root_volume_id)

        ssm.StringParameter(
            self,
            "HPC_ZFS_DNS_NAME_PARAMETER",
            parameter_name=config["parameter_root"] + "/zfs_dns_name",
            string_value=self.hpczfs.attr_dns_name,
        )
