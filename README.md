# aws-mfa-profiles
A package to create credential for AWS using MFA and with the support of multiple profiles

This package wants to simplify the connection to AWS using the MFA supporting also the possibility to use yours profiles.

## Installation
____
You can install the package using `pip install aws-mfa-profiles`.

## Usage
---
There is a little help function callable with `aws-mfa-profiles -h` that it shows this:
```
usage: aws-mfa-profiles [-h] [-p profile] [-t seconds]

Set credential to connect on AWS using MFA

optional arguments:
  -h, --help  show this help message and exit
  -p profile  Profile from which get mfa configuration
  -t seconds  Token expiration time in second from 900 (15 minutes) to 129600 (36 hours) (default: 43200)
```
I set default value for the expiration time session which is `43200` for the expiration time session, this means that the default section is valid for 12 hours. Take in mind that if you use the AWS owner account (root), you can set the session time at maximum at `3600` seconds.

## How does it works?
---
The package read from your `${HOME}/.aws/credentials` file the accounts that you specified and generate a new section in the same file named `${profile_name_selected/choosed}-mfa` with the credentials generated.
Then, you need to define this new account as default for the profiles that you have on `${HOME}/.aws/config`

_credentials_:
```ini
[account_one]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
mfa_serial = YOUR_MFA_ARN

[account_two]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
mfa_serial = YOUR_MFA_ARN

[account_one-mfa]
aws_access_key_id = YOUR_TEMPORARY_ACCESS_KEY_ID
aws_secret_access_key = YOUR_TEMPORARY_SECRET_ACCESS_KEY
aws_session_token = YOUR_TEMPORARY_SESSION_TOKEN

[account_two-mfa]
aws_access_key_id = YOUR_TEMPORARY_ACCESS_KEY_ID
aws_secret_access_key = YOUR_TEMPORARY_SECRET_ACCESS_KEY
aws_session_token = YOUR_TEMPORARY_SESSION_TOKEN
```

_config_:
```ini
[default]
region = eu-west-1
cli_pager=

[profile profile-that-use-mfa-from-account_one]
role_arn = arn:aws:iam::111111111111:role/your_role
source_profile = account_one-mfa

[profile profile-that-use-mfa-from-account_two]
role_arn = arn:aws:iam::222222222222:role/your_role
source_profile = account_two-mfa
```