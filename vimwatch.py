import os
import requests
from github import Github, Auth

import pprint
pp_ = pprint.PrettyPrinter(indent=2)
pp = pp_.pprint

CONFIG = {}
CONFIG['GITHUB_TOKEN'] = os.getenv('VIMWATCH_GITHUB_TOKEN', None)
CONFIG['PUSHOVER_APP_KEY'] = os.getenv('VIMWATCH_PUSHOVER_APP_KEY', None)
CONFIG['PUSHOVER_DEVICE'] = os.getenv('PUSHOVER_DEVICE', None)
CONFIG['PUSHOVER_USER_KEY'] = os.getenv('PUSHOVER_USER_KEY', None)

def main():
    auth = Auth.Token(CONFIG['GITHUB_TOKEN'])
    gh = Github(auth=auth)
    repo = gh.get_repo('vim/vim')

    # get most recent tag on repo
    last_tag = repo.get_tags()[0]

    # extract patch number
    patch_num = last_tag.name.split('.')[2]

    # check if patch will land in homebrew
    if int(patch_num) % 50 == 0:
        # patch is divisible by 50, create pushover notification
        title = f"vim {last_tag.name} released"
        msg = (f"vim patch {last_tag.name} has been released: "
               f"https://github.com/vim/vim/releases/tag/{last_tag.name}")
        r = requests.post('https://api.pushover.net/1/messages.json', data = {
            'token': CONFIG['PUSHOVER_APP_KEY'],
            'user': CONFIG['PUSHOVER_USER_KEY'],
            'message': msg,
            'title': title,
            'device': CONFIG['PUSHOVER_DEVICE']
        })

if __name__ == '__main__':
    main()
