import json
import os
import sys
from datetime import datetime

from . import auth

USERS_CACHE_FNAME = 'user_reg.json'
PACKAGE_NAME = 'pyvlovia'

def test_if_user_cache_exists():
    user_reg_path = os.path.join(get_cache_path(), USERS_CACHE_FNAME)
    return os.path.exists(user_reg_path)


def create_user_cache():
    if not os.path.exists(get_cache_path()):
        os.makedirs(get_cache_path())

    user_reg_path = os.path.join(get_cache_path(), USERS_CACHE_FNAME)
    with open(user_reg_path, 'w') as f:
        json.dump({}, f)


def purge_cache():
    with open(os.path.join(get_cache_path(), USERS_CACHE_FNAME), 'w') as f:
        json.dump({}, f)


def get_cache_path() -> str:
    if sys.platform == 'win32':
        return os.path.join(os.environ['APPDATA'], f'.{PACKAGE_NAME}')
    else:
        return os.path.join(os.environ['HOME'], f'.{PACKAGE_NAME}')


def add_user_to_cache(username, token):
    user_data = dict(
        username=username, access_token=token,
        registeration_date=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    with open(os.path.join(get_cache_path(), USERS_CACHE_FNAME), 'r+') as f:
        cache = json.load(f)

    if username not in cache:
        with open(os.path.join(get_cache_path(), USERS_CACHE_FNAME), 'w') as f:
            cache[username] = user_data
            json.dump(cache, f)


def remove_user_from_cache(user):
    with open(os.path.join(get_cache_path(), USERS_CACHE_FNAME), 'r+') as f:
        cache = json.load(f)

    if user in cache:
        cache.pop(user)

    with open(os.path.join(get_cache_path(), USERS_CACHE_FNAME), 'w') as f:
        json.dump(cache, f)


def load_available_users():
    user_reg_path = os.path.join(get_cache_path(), USERS_CACHE_FNAME)
    with open(user_reg_path) as f:
        _json = json.load(f)
    return _json.keys()

def load_token_for_user(user):
    user_reg_path = os.path.join(get_cache_path(), USERS_CACHE_FNAME)

    with open(user_reg_path) as f:
        _json = json.load(f)

    return _json[user][auth.TOKEN_KEY_NAME]