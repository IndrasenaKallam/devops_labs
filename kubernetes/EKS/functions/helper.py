import boto3

def get_account_number():
    """
    Fetch the AWS account number dynamically using the STS client.
    :return: AWS account number as a string.
    """
    sts_client = boto3.client('sts')
    account_id = sts_client.get_caller_identity()["Account"]
    return account_id

