import requests

TOKEN_KEY_NAME = 'access_token'


def get_token(gitlab_username, gitlab_password):
    data = {'grant_type': 'password',
            'username': gitlab_username, 'password': gitlab_password,
            }
    resp = requests.post('https://gitlab.pavlovia.org/oauth/token?scope=read_user', data=data)

    resp_data = resp.json()
    gitlab_oauth_token = resp_data[TOKEN_KEY_NAME]
    return gitlab_oauth_token
