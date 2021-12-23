from boto3 import session as boto3_session
from botocore.session import Session as botocore_session
from os import environ as os_environ
import argparse
import configparser
import logging

logging.basicConfig(format='{"timestamp":"%(asctime)s", "level":"%(levelname)s", "message":"%(message)s"}')
parser = argparse.ArgumentParser(description='Set credential to connect on AWS using MFA')
parser.add_argument('-p', metavar='profile', default='profile', help='Profile from which get mfa configuration (default: %(default)s)')
parser.add_argument('-t', metavar='seconds', type=int, default=43200, choices=range(900, 129600),
                    help='Token expiration time in second from 900 (15 minutes) to 129600 (36 hours) (default: %(default)s)')


def check_token_validation(prompt: str):
    if prompt.isdecimal() and 6 <= len(prompt):
        logging.info('Token has at least 6 characters, this is ok')
        logging.info('Token is only numerical, this is ok')
        return
    else:
        logging.error('Token is invalid!')
        quit(code=1)


def generate_credentials(aws_account_name: str, aws_token_validity: int, token: str):
    mfa_session = botocore_session(profile=aws_account_name)
    mfa_serial = mfa_session.get_scoped_config().get('mfa_serial')
    client = generate_client_session(aws_account_name)
    try:
        response = client.get_session_token(
            DurationSeconds=aws_token_validity,
            SerialNumber=mfa_serial,
            TokenCode=token
        )
        return response
    except Exception as e:
        logging.error(e)
        quit(code=1)


def generate_client_session(aws_account_name: str):
    session = boto3_session.Session(
        profile_name=aws_account_name
    )
    client = session.client('sts')
    return client


def set_aws_variables(credentials):
    config = configparser.ConfigParser()
    config.read('{}/.aws/credentials'.format(os_environ['HOME']))
    try:
        config.remove_section('temporary-credentials-with-mfa')
    except Exception as e:
        logging.info('No section to delete ', e)
    config.add_section('temporary-credentials-with-mfa')
    config['temporary-credentials-with-mfa']['aws_access_key_id'] = credentials['Credentials']['AccessKeyId']
    config['temporary-credentials-with-mfa']['aws_secret_access_key'] = credentials['Credentials']['SecretAccessKey']
    config['temporary-credentials-with-mfa']['aws_session_token'] = credentials['Credentials']['SessionToken']
    with open('{}/.aws/credentials'.format(os_environ['HOME']), 'w') as configfile:
        config.write(configfile)


def main():
    args = parser.parse_args()
    aws_account_name = args.p
    aws_token_validity = args.t
    token = input("Insert MFA token: ")
    check_token_validation(token)
    response = generate_credentials(aws_account_name, aws_token_validity, token)
    set_aws_variables(response)


if __name__ == '__main__':
    main()
