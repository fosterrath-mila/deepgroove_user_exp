#!/usr/bin/env python3

import os
import json
import argparse

# Parse the command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", default='deepgroove_web_user_experiment/static/data')
args = parser.parse_args()

users = []

assert os.path.exists(args.data_dir)

for root, dirs, files in os.walk(args.data_dir, topdown=False):
    for dir_name in sorted(dirs):
        dir_path = os.path.join(root, dir_name)
        json_path = os.path.join(root, dir_name, 'data.json')
        model_path = os.path.join(root, dir_name, 'model_080.pt')

        if not os.path.exists(json_path):
            print('WARNING: json file missing for "{}"'.format(dir_path))
            continue
        if not os.path.exists(model_path):
            print('WARNING: model_080.pt missing for "{}"'.format(dir_path))
            continue

        with open(json_path) as f:
            data = json.load(f)

        user_email = data['user_email']
        user_name = data['user_name']        

        if user_email in users:
            print('WARNING: multiple entries for user {}'.format(user_email))

        users.append((dir_name, user_email, user_name))

print('Got data for {} users:'.format(len(users)))
for dir_name, user_email, user_name in users:
    print('{}: {}, {}'.format(dir_name, user_email, user_name))
