# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_fsx as fsx,
    aws_s3 as s3,
    aws_ssm as ssm,
    CfnOutput,
    RemovalPolicy,
)


class HpcLustreStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc, config: dict, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        lustre_subnet = vpc.private_subnets[0]

        self.hpclustre_sg = ec2.SecurityGroup(
            self,
            "HPC_SG_LUSTRE",
            vpc=vpc,
            allow_all_outbound=True,
        )

        self.hpclustre_sg.add_ingress_rule(
            self.hpclustre_sg,
            ec2.Port.tcp(988),
            "Allows Lustre traffic between FSx for Lustre file servers",
        )
        self.hpclustre_sg.add_ingress_rule(
            self.hpclustre_sg,
            ec2.Port.tcp_range(1018, 1023),
            "Allows Lustre traffic between FSx for Lustre file servers",
        )

        lustre_config = fsx.LustreConfiguration(
            deployment_type=fsx.LustreDeploymentType.PERSISTENT_2,
            data_compression_type=fsx.LustreDataCompressionType.LZ4,
            per_unit_storage_throughput=config["lustre"]["throughput"],
        )

        self.hpclustre = fsx.LustreFileSystem(
            self,
            "HPC_LUSTRE",
            vpc=vpc,
            security_group=self.hpclustre_sg,
            vpc_subnet=lustre_subnet,
            storage_capacity_gib=config["lustre"]["capacity"],
            lustre_configuration=lustre_config,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.hpcbucket = s3.Bucket(
            self,
            "HPC_S3B",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            enforce_ssl=True,
        )

        self.hpcdra = fsx.CfnDataRepositoryAssociation(
            self,
            "HPC_DRA",
            data_repository_path=f"s3://{self.hpcbucket.bucket_name}/lustre/",
            file_system_id=self.hpclustre.file_system_id,
            file_system_path="/",
            batch_import_meta_data_on_create=True,
            imported_file_chunk_size=1024,
            s3=fsx.CfnDataRepositoryAssociation.S3Property(
                auto_export_policy=fsx.CfnDataRepositoryAssociation.AutoExportPolicyProperty(
                    events=["NEW", "CHANGED", "DELETED"],
                ),
                auto_import_policy=fsx.CfnDataRepositoryAssociation.AutoImportPolicyProperty(
                    events=["NEW", "CHANGED", "DELETED"],
                ),
            ),
        )

        CfnOutput(self, "LustreFileSystemId", value=self.hpclustre.file_system_id)

        ssm.StringParameter(
            self,
            "HPC_LUSTRE_MOUNT_NAME_PARAMETER",
            parameter_name=config["parameter_root"] + "/lustre_mount_name",
            string_value=self.hpclustre.mount_name,
        )

        ssm.StringParameter(
            self,
            "HPC_LUSTRE_DNS_NAME_PARAMETER",
            parameter_name=config["parameter_root"] + "/lustre_dns_name",
            string_value=self.hpclustre.dns_name,
        )
