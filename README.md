# aws-windows-keypair

## What it does
Takes an AWS Region (e.g. eu-west-2) and an EC2 Key Pair name and checks to see if the Key Pair exists.  
If the Key Pair exists, no further activity occurs.  
If the Key Pair doesn't exist the script will create one, then create an AWS Secret containing the Private RSA key.  

## Why it was created
I needed to create a Key Pair for a Windows AMI AutoScaling group. Terraform requires you to have a public key to use as a base for a Key Pair it creates but I wanted something self-contained within AWS.  
