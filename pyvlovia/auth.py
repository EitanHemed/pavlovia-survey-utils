import requests

TOKEN_KEY_NAME = 'access_token'
REQUEST_POST_URL = 'https://gitlab.pavlovia.org/oauth/token?scope=read_user'


def get_pavlovia_access_token(gitlab_username: str, gitlab_password: str) -> str:
    """
    Retrieve Gitlab access token for the Pavlovia projects availalbe to the user.
    :param str gitlab_username: Gitlab username
    :param str gitlab_password: Gitlab password
    :return: Access token for Pavlovia projects available to the user.
    :rtype: str
    """

    data = {'grant_type': 'password', 'username': gitlab_username, 'password': gitlab_password}
    resp = requests.post(REQUEST_POST_URL, data=data)
    resp_data = resp.json()
    gitlab_oauth_token = resp_data[TOKEN_KEY_NAME]
    return gitlab_oauth_token
