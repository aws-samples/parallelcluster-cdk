# ParallelCluster in CDK

Example deployment using the CFn custom resource functionality added to ParallelCluster in version 3.6.0.

The file `config.json` provides a convenient location to store and update variables which might be used throughout the app.

Configuration parameters used by default:
- `label`: Used to name the ParallelCluster deployment stack
- `key_name`: The name given to the SSH key when added to your account
- `key_material`: The contents of the SSH public key you want to add for use with ParallelCluster
- `parameter_root`: Prefix for SSM parameters deployed by the solution
- `trusted_cidr`: IP range added to the ParallelCluster controller security group ingress rule

### Setup

1. Clone the repository
2. Update the `local.env` file to include the account/region you wish to deploy to, and the app config file you want to target for deployment
3. Run `source local.env` to make account/region environment variables available to CDK
4. Follow the [official CDK documentation](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html) to make the target account/region ready for CDK deployment (`cdk bootstrap`)
5. Update the config file (`config.json` by default) to reflect changes to the configuration you would like to make
7. Deploy the cluster and its supporting infrastructure (VPC, storage etc) with `cdk deploy`
8. Verify that the cluster is accessible via SSH/SSM, and that mount points are working correctly
9. When finished, remove the cluster and its supporting infrastructure using `cdk destroy`

### Architecture

![ParallelCluster CDK deployment architecture diagram](pcluster-cdk.png)