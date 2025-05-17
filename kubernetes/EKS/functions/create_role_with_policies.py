import boto3
import json


def create_iam_role(role_name, trust_policy, policies, tags=None):
    """
    Create an IAM role and attach policies to it.

    :param role_name: Name of the IAM role to create.
    :param trust_policy: Trust policy document as a dictionary.
    :param policies: List of policy ARNs to attach to the role.
    :param tags: List of tags to add to the role (optional).
    """
    iam_client = boto3.client('iam')

    # Create the IAM role
    try:
        iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Tags=tags or []
        )
        print(f"Role '{role_name}' created successfully.")
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"Role '{role_name}' already exists.")
    except Exception as e:
        print(f"Error creating role: {e}")
        return

    # Attach the policies to the role
    for policy_arn in policies:
        try:
            iam_client.attach_role_policy(
                RoleName=role_name,
                PolicyArn=policy_arn
            )
            print(f"Policy '{policy_arn}' attached to role '{role_name}' successfully.")
        except Exception as EntityAlreadyExistsException:
            print(f"Policy '{policy_arn}' already attached to role '{role_name}'.")
        except Exception as e:
            print(f"Error attaching policy '{policy_arn}': {e}")