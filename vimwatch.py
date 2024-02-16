import os
import requests
from github import Github, Auth

import pprint
pp_ = pprint.PrettyPrinter(indent=2)
pp = pp_.pprint

SCRIPTPATH = os.path.dirname(os.path.realpath(__file__))

CONFIG = {}
CONFIG['GITHUB_TOKEN'] = os.getenv('VIMWATCH_GITHUB_TOKEN', None)
CONFIG['PUSHOVER_APP_KEY'] = os.getenv('VIMWATCH_PUSHOVER_APP_KEY', None)
CONFIG['PUSHOVER_DEVICE'] = os.getenv('PUSHOVER_DEVICE', None)
CONFIG['PUSHOVER_USER_KEY'] = os.getenv('PUSHOVER_USER_KEY', None)

def main():
    auth = Auth.Token(CONFIG['GITHUB_TOKEN'])
    gh = Github(auth=auth)
    repo = gh.get_repo('vim/vim')

    # read last notified patch value from file
    with open(SCRIPTPATH + '/last_notified.cache', 'r') as CACHEFILE:
        raw = CACHEFILE.read()

    if raw == '':
        notified_patch = 0
    else:
        notified_patch = int(raw.strip().split('.')[2])

    # get most recent tag on repo
    last_tag = repo.get_tags()[0]

    # extract semver parts
    parts = last_tag.name.split('.')
    major = parts[0][1:]
    minor = parts[1]
    patch_num = int(parts[2])

    # check if patch is after a new release in homebrew
    next_release = notified_patch + 50
    if patch_num >= next_release:
        latest_release_patch = patch_num - (patch_num % 50)
        latest_release = f"v{major}.{minor}.{str(latest_release_patch).zfill(4)}"

        # create pushover notification
        title = f"vim {latest_release} released"
        msg = (f"vim {latest_release} has been released: "
               f"https://github.com/vim/vim/releases/tag/{latest_release}")
        r = requests.post('https://api.pushover.net/1/messages.json', data = {
            'token': CONFIG['PUSHOVER_APP_KEY'],
            'user': CONFIG['PUSHOVER_USER_KEY'],
            'message': msg,
            'title': title,
            'device': CONFIG['PUSHOVER_DEVICE']
        })

        with open(SCRIPTPATH + '/last_notified.cache', 'w') as CACHEFILE:
            CACHEFILE.write(latest_release)

if __name__ == '__main__':
    main()
