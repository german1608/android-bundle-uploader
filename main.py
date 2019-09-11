#!env/bin/python
from google.oauth2 import service_account
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('service_account_file', type=str, help='Service Account file in json format')
args = parser.parse_args()

SERVICE_ACCOUNT_FILE = args.service_account_file

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE)

scoped_credentials = credentials.with_scopes(
    ['https://www.googleapis.com/auth/cloud-platform'])
