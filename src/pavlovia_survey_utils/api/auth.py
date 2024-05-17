"""
This module includes functions related to retriving and storing user access tokens for Pavlovia.
"""

import json
import os
import sys
import typing
import warnings
from datetime import datetime

import requests

USERS_CACHE_FNAME = 'reg.json'
PACKAGE_NAME = 'pavlovia_surveys_utils'

TOKEN_KEY_NAME = 'access_token'
REQUEST_POST_URL = 'https://gitlab.pavlovia.org/oauth/token?scope=read_user'

REGISTRATION_DATE_KEY_NAME = 'registration_date'

__all__ = ['load_available_users', 'add_user_to_cache', 'purge_cache', 'remove_user_from_cache', 'load_token_for_user']

def _get_timestamp() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def add_user_to_cache(username: str, password: str,
                      force_update:bool = False) -> None:
    """
    Register a user in the saved users cache.

    :param username: The username on Pavlovia.
    :param password: The password of the user.
    :param force_update: If True, the user will be updated if they already exist.
    :return:
    """
    user_reg_path = _get_user_reg_path()
    token = get_pavlovia_access_token(username, password)

    user_data = {
        TOKEN_KEY_NAME: token,
        REGISTRATION_DATE_KEY_NAME: _get_timestamp()
    }

    with open(user_reg_path, 'r') as f:
        cache = json.load(f)

    if (username not in cache) or force_update:
        # Overwrite the user data.
        with open(user_reg_path, 'w') as f:
            cache[username] = user_data
            _json = json.dumps(cache)
            f.write(_json)
    else:
        warnings.warn(f"User {username} already exists in cache. "
                          f"Please pass `force_update=True`.")

def remove_user_from_cache(user) -> str:
    """
    Remove a user from the cache.
    :param user: The username of the user to remove.
    :return: bool: True if the user was removed, False otherwise.
    """
    user_found_and_removed = False

    user_reg_path = _get_user_reg_path()

    with open(user_reg_path, 'r+') as f:
        cache = json.load(f)

    if user in cache:
        cache.pop(user)
        user_found_and_removed = True

    with open(user_reg_path, 'w') as f:
        json.dump(cache, f)

    return user_found_and_removed

def load_available_users() -> typing.List[str]:
    """
    Get a list of all the users in the cache.
    :return:
        list: A list of all the usernames in the cache.
    """
    with open(_get_user_reg_path()) as f:
        _json = json.load(f)
    return list(_json.keys())

def purge_cache() -> None:
    """
    Remove all users from the cache.
    :return:
    """
    # Remove the cache file.
    os.remove(_get_user_reg_path())

def load_token_for_user(user: str) -> str:
    """
    Get the access token for a user.
    :param user: The username of the user.
    :return: str: The access token for the user.

    :raises FileNotFoundError: If the registry file is not found.
            KeyError: If the user is not found in the registry.
    """
    with open(_get_user_reg_path()) as f:
        _json = json.load(f)

    return _json[user][TOKEN_KEY_NAME]

def _get_cache_path() -> str:
    if sys.platform == 'win32':
        return os.path.join(os.environ['APPDATA'], f'.{PACKAGE_NAME}')
    else:
        return os.path.join(os.environ['HOME'], f'.{PACKAGE_NAME}')

def _get_user_reg_path():
    return os.path.join(_get_cache_path(), USERS_CACHE_FNAME)

def _test_if_user_cache_exists():
    return os.path.exists(_get_user_reg_path())

def _create_user_cache() -> None:
    if not os.path.exists(_get_cache_path()):
        os.makedirs(_get_cache_path())

    with open(_get_user_reg_path(), 'w') as f:
        json.dump({}, f)

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
    try:
        gitlab_oauth_token = resp_data[TOKEN_KEY_NAME]
    except KeyError as e:
        raise KeyError(f"Please check the username and password.") from e

    return gitlab_oauth_token
