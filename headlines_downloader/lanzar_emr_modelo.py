import boto3

def lambda_handler(event, context):
    client = boto3.client('emr', region_name='us-east-1')

    cluster_response = client.run_job_flow(
        Name='cluster-ml-noticias',
        ReleaseLabel='emr-6.15.0',
        Applications=[{'Name': 'Spark'}],
        Instances={
            'InstanceGroups': [
                {
                    'Name': 'Master node',
                    'Market': 'ON_DEMAND',
                    'InstanceRole': 'MASTER',
                    'InstanceType': 'm5.xlarge',
                    'InstanceCount': 1,
                }
            ],
            'KeepJobFlowAliveWhenNoSteps': False,
            'TerminationProtected': False
        },
        JobFlowRole='EMR_EC2_DefaultRole',
        ServiceRole='EMR_DefaultRole',
        VisibleToAllUsers=True,
        LogUri='s3://headlinesjune/logs/',
        Steps=[
            {
                'Name': 'Ejecutar modelo de noticias',
                'ActionOnFailure': 'TERMINATE_CLUSTER',
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': [
                        'spark-submit',
                        '--deploy-mode', 'cluster',
                        's3://headlinesjune/scripts/model.py'
                    ]
                }
            }
        ]
    )

    return {
        'message': 'Cluster lanzado con ID: ' + cluster_response['JobFlowId']
    }
