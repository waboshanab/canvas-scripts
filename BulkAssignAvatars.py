# Bulk Assign Avatars - 11-15-2022
"""
Requirements:
pip3 install requests
certifi==2019.9.11/chardet==3.0.4/idna==2.8/requests==2.22.0/urllib3==1.25.6
"""

import requests
import csv
import time
import os
import os.path
import json
import collections
import mimetypes
import pprint
import sys

# Base working path of this script, where everything will be housed.
working_path = 'PATH'
# This is the name of the folder that houses the images.
images_path = 'images/'
domain = '{domain}.instructure.com'  # Replace domain
access_token = "TOKEN"


header = {'Authorization': 'Bearer {0}'.format(access_token)}
valid_mimetypes = ('image/jpeg', 'image/png', 'image/gif')
ext = ('.jpg', '.jpeg', '.png', '.gif')

for file in os.scandir(f"{working_path}{images_path}"):
    if file.is_file():
        if file.path.endswith(ext):
            # Step 1: Start upload file to user's file storage in Canvas
            inform_api_url = f"https://{domain}/api/v1/users/self/files"
            image_path = f"{working_path}{images_path}{file.name}"
            mime_type = mimetypes.guess_type(image_path)
            user_id = file.name.split('.', 1)[0]
            inform_parameters = {
                'name': file.name,
                'content_type': mime_type,
                'size': os.path.getsize(image_path),
                'parent_folder_path': 'profile pictures',
                'as_user_id': f"sis_user_id:{user_id}"
            }
            res = requests.post(
                inform_api_url, headers=header, data=inform_parameters)
            if res.status_code != 200:
                print(
                    f'Error: No user found for {user_id} - file name:{file.name} - type:{mime_type}')
            else:
                data = res.json()

                # Step 2:  Upload data
                files = {'file': open(image_path, 'rb').read()}
                upload_params = data.get('upload_params')
                upload_url = data.get('upload_url')
                upload_file_res = requests.post(
                    upload_url, data=upload_params, files=files, allow_redirects=False)

                # Step 3: Confirm upload
                confirmation_url = upload_file_res.headers['location']
                confirmation = requests.post(confirmation_url, headers=header)
                if 'id' in confirmation.json():
                    file_id = confirmation.json()['id']
                else:
                    print('no id here')
                params = {'as_user_id': f"sis_user_id:{user_id}"}

                # Step 4: Find recently uploaded image and get the user token
                avatar_options = requests.get(
                    f"https://{domain}/api/v1/users/sis_user_id:{user_id}/avatars", headers=header, params=params)

                for ao in avatar_options.json():
                    if ao.get('display_name') == file.name:
                        token = ao.get('token')
                        params['user[avatar][token]'] = token
                        set_avatar_user = requests.put(
                            f"https://{domain}/api/v1/users/sis_user_id:{user_id}", headers=header, params=params)
                        if set_avatar_user.status_code == 200:
                            print(f'Profile image set for user - {user_id}')
                        else:
                            print(
                                f'Failed to set profile image for user - {user_id}')


print('Done')
