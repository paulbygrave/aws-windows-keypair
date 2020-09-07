# aws-windows-keypair

## What it does
Takes an AWS Region (e.g. eu-west-2) and an EC2 Key Pair name and checks to see if the Key Pair exists.  
If the Key Pair exists, no further activity occurs.  
If the Key Pair doesn't exist the script will create one, then create an AWS Secret containing the Private RSA key.  

## Why it was created
I needed to create a Key Pair for a Windows AMI AutoScaling group. Terraform requires you to have a public key to use as a base for a Key Pair it creates but I wanted something self-contained within AWS.  

## Usage
python3 windows-keypair.py -h                                                                 
usage: windows-keypair.py [-h] [-r ROLE_ARN] region keypair

The optional ROLE_ARN flag can be invoked with either '-r' or '--role-arn'.
The "region" argument must be passed in "Terraform" format, e.g. "eu-west-2".
The "keypair" argument is the name of the Key Pair you want to create, and forms the basis for the Secret name as well. Must follow normal AWS naming standards.
