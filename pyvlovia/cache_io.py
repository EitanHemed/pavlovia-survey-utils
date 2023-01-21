import json
import os
import sys
from datetime import datetime

from . import auth

USERS_CACHE_FNAME = 'user_reg.json'
PACKAGE_NAME = 'pyvlovia'

__all__ = ['load_available_users', 'add_user_to_cache', 'purge_cache', 'remove_user_from_cache', 'load_token_for_user']


def add_user_to_cache(username, password):
    user_reg_path = _get_user_reg_path()

    token = auth.get_pavlovia_access_token(username, password)

    user_data = dict(
        username=username, access_token=token,
        registeration_date=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    with open(user_reg_path, 'r+') as f:
        cache = json.load(f)

    if username not in cache:
        with open(user_reg_path, 'w') as f:
            cache[username] = user_data
            json.dump(cache, f)


def remove_user_from_cache(user) -> str:
    res = f'User {user} not found!'

    user_reg_path = _get_user_reg_path()

    with open(user_reg_path, 'r+') as f:
        cache = json.load(f)

    if user in cache:
        cache.pop(user)
        res = f'Removed {user} from cache!'

    with open(user_reg_path, 'w') as f:
        json.dump(cache, f)

    return res

def load_available_users() -> list:
    with open(_get_user_reg_path()) as f:
        _json = json.load(f)
    return list(_json.keys())

def purge_cache():
    with open(_get_user_reg_path(), 'w') as f:
        json.dump({}, f)

def load_token_for_user(user):
    with open(_get_user_reg_path()) as f:
        _json = json.load(f)

    return _json[user][auth.TOKEN_KEY_NAME]

def _get_cache_path() -> str:
    if sys.platform == 'win32':
        return os.path.join(os.environ['APPDATA'], f'.{PACKAGE_NAME}')
    else:
        return os.path.join(os.environ['HOME'], f'.{PACKAGE_NAME}')

def _get_user_reg_path():
    return os.path.join(_get_cache_path(), USERS_CACHE_FNAME)


def _test_if_user_cache_exists():
    return os.path.exists(_get_user_reg_path())


def _create_user_cache():
    if not os.path.exists(_get_cache_path()):
        os.makedirs(_get_cache_path())

    with open(_get_user_reg_path(), 'w') as f:
        json.dump({}, f)