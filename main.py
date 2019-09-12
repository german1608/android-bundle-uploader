#!env/bin/python
import argparse

import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

parser = argparse.ArgumentParser()
parser.add_argument('service_account_file', type=str, help='Service Account file in json format')
parser.add_argument('package_name', type=str, help='Package Name of the app bundle')
parser.add_argument('aab_file', type=str, help='Path of the Android App Bundle file')
parser.add_argument('track', choices=['production', 'alpha', 'beta', 'internal'], default='internal',
                    help='Track to upload the apk to')
args = parser.parse_args()

SERVICE_ACCOUNT_FILE = args.service_account_file
PACKAGE_NAME = args.package_name
APP_BUNDLE_FILE = args.aab_file
TRACK = args.track

# Load credentials
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    SERVICE_ACCOUNT_FILE, scopes='https://www.googleapis.com/auth/androidpublisher')
http = httplib2.Http()
http = credentials.authorize(http)

# Create the service
service = build('androidpublisher', 'v2', http)

edit_id = None
try:
    edit_request = service.edits().insert(body={}, packageName=PACKAGE_NAME)
    result = edit_request.execute()
    edit_id = result['id']

    aab_response = service.edits().bundles().upload(
        editId=edit_id,
        packageName=PACKAGE_NAME,
        media_mime_type='application/octet-stream',
        media_body=APP_BUNDLE_FILE).execute()
    print('Android App Bundle with {} version code has been uploaded'.format(aab_response['versionCode']))

    track_response = service.edits().tracks().update(
        editId=edit_id,
        track=TRACK,
        packageName=PACKAGE_NAME,
        body={'versionCodes': [aab_response['versionCode']]}).execute()
    print('Track {} is set for version code(s) {}'.format(TRACK, track_response['versionCodes']))

    commit_request = service.edits().commit(
        editId=edit_id, packageName=PACKAGE_NAME).execute()

    print('Edit #{} has been committed'.format(commit_request['id']))
except Exception as e:
    delete_edit_response = service.edits().delete(
        editId=edit_id, packageName=PACKAGE_NAME).execute()
    print(e)
