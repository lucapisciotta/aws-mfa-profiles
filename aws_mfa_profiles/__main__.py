"""Module for AWS MFA credentials management"""
import argparse
import configparser
import logging
from os import environ as os_environ
from sys import exit as sys_exit
import botocore.exceptions
from boto3 import session as boto3_session
from botocore.session import Session as botocore_session
from inquirer import List as inquirer_list, prompt as inquirer_prompt


logging.basicConfig(format='%(levelname)s - %(message)s')
parser = argparse.ArgumentParser(description='Set credential to connect on AWS using MFA')
parser.add_argument('-p', metavar='profile', help='Profile from which get mfa configuration')
parser.add_argument('-t', metavar='seconds', type=int, default=43200, choices=range(900, 129600),
    help='Token expiration time in second from 900 (15 minutes) to 129600 (36 hours) (default: %(default)s)')
sections_list = []
credential_file = configparser.ConfigParser()
try:
    credential_file.read(f'{os_environ["HOME"]}/.aws/credentials')
except configparser.Error:
    logging.error('%s/.aws/credentials', os_environ['HOME'])
    sys_exit(1)


def check_profile_exists(profile: str):
    """Function to check if the provided profile exists"""
    if not credential_file.has_section(profile):
        logging.error('%s doesn\'t exists in your credentials file', profile)
        sys_exit(1)


def check_profile_mfa(profile: str):
    """"Function to check if the provided profile has the mfa"""
    if not credential_file.has_option(profile, 'mfa_serial'):
        logging.error('%s haven\'t got the mfa_serial defined in the credential file', profile)
        sys_exit(1)


def check_token_validation(prompt: str):
    """Function to check if the provided tocken is valid"""
    if prompt.isdecimal() and 6 <= len(prompt):
        logging.info('Token has at least 6 characters, this is ok')
        logging.info('Token is only numerical, this is ok')
    else:
        logging.error('Token is invalid!')
        sys_exit(1)


def generate_credentials(profile: str, aws_token_validity: int, token: str):
    """Function to generate the credentials with MFA"""
    mfa_session = botocore_session(profile=profile)
    mfa_serial = mfa_session.get_scoped_config().get('mfa_serial')
    client = generate_client_session(profile)
    try:
        response = client.get_session_token(
            DurationSeconds=aws_token_validity,
            SerialNumber=mfa_serial,
            TokenCode=token
        )
        return response
    except botocore.exceptions.ClientError as error:
        logging.error('Ops, you encounter an exception: %s', error.response['Error']['Code'])
        return None


def generate_client_session(profile: str):
    """Function to create a client session"""
    session = boto3_session.Session(
        profile_name=profile
    )
    client = session.client('sts')
    return client


def read_profiles():
    """Function to read the valid profile in the credentials file"""
    try:
        sections = credential_file.sections()
        for section in sections:
            if '-mfa' in section:
                continue
            if not credential_file.has_option(section, 'mfa_serial'):
                continue
            sections_list.append(section)
    except configparser.Error:
        logging.error('Something goes wrong during the read_profiles function')


def set_aws_variables(profile: str, credentials):
    """Function to add the temporary credential to the credentials file"""
    section_name = f'{profile}-mfa'
    try:
        credential_file.remove_section(section_name)
    except configparser.NoSectionError:
        logging.warning('No section %s to delete ', section_name)
    credential_file.add_section(section_name)
    credential_file[section_name]['aws_access_key_id'] = credentials['Credentials']['AccessKeyId']
    credential_file[section_name]['aws_secret_access_key'] = credentials['Credentials']['SecretAccessKey']
    credential_file[section_name]['aws_session_token'] = credentials['Credentials']['SessionToken']
    with open(f'{os_environ["HOME"]}/.aws/credentials', encoding="utf-8", mode='w') as configfile:
        credential_file.write(configfile)


def main():
    """Main function"""
    args = parser.parse_args()
    profile = args.p
    aws_token_validity = args.t
    if not profile:
        read_profiles()
        profiles_list = [inquirer_list('profile_name',
            message='Choose the profile from which create temporary MFA credentials',
            choices=sections_list)]
        selected_profile = inquirer_prompt(profiles_list)
        if not selected_profile:
            sys_exit(1)
        profile = selected_profile['profile_name']
    check_profile_exists(profile)
    check_profile_mfa(profile)
    token = input("Insert MFA token: ")
    check_token_validation(token)
    response = generate_credentials(profile, aws_token_validity, token)
    if not response:
        sys_exit(1)
    set_aws_variables(profile, response)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
