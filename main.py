#!env/bin/python
import argparse

import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('service_account_file', type=str, help='Service Account file in json format')
    parser.add_argument('package_name', type=str, help='Package Name of the app bundle')
    parser.add_argument('aab_file', type=str, help='Path of the Android App Bundle file')
    parser.add_argument('track', choices=['production', 'alpha', 'beta', 'internal'], default='internal',
                        help='Track to upload the apk to')
    args = parser.parse_args()

    service_account_file = args.service_account_file
    package_name = args.package_name
    app_bundle_file = args.aab_file
    track = args.track

    # Load credentials
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        service_account_file, scopes='https://www.googleapis.com/auth/androidpublisher')
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Create the service
    service = build('androidpublisher', 'v3', http)

    edit_id = None
    try:
        edit_request = service.edits().insert(body={}, packageName=package_name)
        result = edit_request.execute()
        edit_id = result['id']

        aab_response = service.edits().bundles().upload(
            editId=edit_id,
            packageName=package_name,
            media_mime_type='application/octet-stream',
            media_body=app_bundle_file).execute()
        print('Android App Bundle with {} version code has been uploaded'.format(aab_response['versionCode']))

        track_response = service.edits().tracks().update(
            editId=edit_id,
            track=track,
            packageName=package_name,
            body={'versionCodes': [aab_response['versionCode']]}).execute()
        print('Track {} is set for version code(s) {}'.format(track, track_response['versionCodes']))

        commit_request = service.edits().commit(
            editId=edit_id, packageName=package_name).execute()

        print('Edit #{} has been committed'.format(commit_request['id']))
    except Exception as e:
        service.edits().delete(
            editId=edit_id, packageName=package_name).execute()
        print(e)


if __name__ == '__main__':
    main()
