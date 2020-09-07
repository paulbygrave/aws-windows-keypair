import boto3
from boto3.session import Session
from botocore.exceptions import ClientError
import argparse
import sys

# Define the arguments
parser = argparse.ArgumentParser(description='Check if a keypair exists in AWS, if not create it and commit Private Key string to an AWS Secret.')
parser.add_argument('-r', '--role-arn', required=False, help='The Role ARN to be assumed, if required.')
parser.add_argument('region', help='The AWS region to create the resources in.')
parser.add_argument('keypair', help='The name of the Key Pair you wish to create.')

# Load the argument values
args = parser.parse_args()

# Set variable values to the argument values
role_arn=args.role_arn
aws_region=args.region
keypair_name=args.keypair

# Create a generic session name
session_name="keypair-session"

# Function to get current role
def get_role():
    client = boto3.client('sts')
    user_arn = client.get_caller_identity()["Arn"]
    print(f'The current identity is "{user_arn}".')  

# Function to assume the role
def assume_role(arn, session_name):
    client = boto3.client('sts')
    account_id = client.get_caller_identity()["Account"]
    user_arn = client.get_caller_identity()["Arn"]
    print(f'{role_arn} passed as argument. Assuming role...')  
    response = client.assume_role(RoleArn=arn, RoleSessionName=session_name)    
    session = Session(aws_access_key_id=response['Credentials']['AccessKeyId'],
                      aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                      aws_session_token=response['Credentials']['SessionToken'])   
    client = session.client('sts')
    account_id = client.get_caller_identity()["Account"]
    user_arn = client.get_caller_identity()["Arn"]
    print(f'Role "{user_arn}" assumed, commencing keypair activities...')  

# Function to check whether the Key Pair exists
def check_keypair(key_name):
    ec2 = boto3.client('ec2', region_name=f'{aws_region}')
    response = ec2.describe_key_pairs(
        KeyNames=[key_name,]
    )

# Function to create the Key Pair
def create_keypair(key_name):
    ec2 = boto3.client('ec2', region_name=f'{aws_region}')
    response = ec2.create_key_pair(KeyName=key_name)
    key_content = response['KeyMaterial']
    # Print out the key content, suppressed for security
    #print(key_content)
    return key_content

# Function to create the secret
def create_secret(key_content):
    secrets = boto3.client('secretsmanager', region_name=f'{aws_region}')
    response = secrets.create_secret(
    Description=f'Private RSA key for the Key Pair "{keypair_name}".',
    Name=f'{keypair_name}-private-key-data',
    SecretString=f'{key_content}',
    )
    secret_arn = response['ARN']
    return secret_arn

# The main script which utilises the functions above
# Set a loop
while True:
    # Print the current identity
    get_role()
    # Invoke assume role function if argument was passed to do so
    if role_arn:
        assume_role(role_arn, session_name)
    else:
        print('No alternate role provided, commencing keypair activities... ')
    # Check for an existing keypair using the value specified, exit with no further action if Key Pair exists
    try:
        check_keypair(keypair_name)
        print(f'The Key Pair "{keypair_name}" already exists, no action required!')
        break
    # If Key Pair is not found, proceed
    except ClientError as e:
        # If Key Pair check fails because key does not exist, proceed
        if e.response['Error']['Code'] == 'InvalidKeyPair.NotFound':
            print(f'The Key Pair "{keypair_name}" doesn\'t exist, creating keypair...')
            # Attempt to create Key Pair
            try:
                key_content = create_keypair(keypair_name)
                print(f'The Key Pair "{keypair_name}" was created successfully! Attempting to write to Secrets Manager...')
                # If creation of Key Pair successful, attempt to write to Secret
                try:
                    secret_arn = create_secret(key_content)
                    print(f'The Key Pair "{keypair_name}" was created successfully and written to AWS Secrets Manager as "{secret_arn}".')
                    break
                # If creation of Secret fails, exit
                except ClientError as e:
                    print(e.response['Error']['Code'])
                    sys.exit(4)
            # If creation of Key Pair fails, exit
            except ClientError as e:
                print(e.response['Error']['Code'])
                sys.exit(3)
        # If Key Pair check fails for any other reason, exit
        else:
            print(e.response['Error']['Code'])
            sys.exit(2)
