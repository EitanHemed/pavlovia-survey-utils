import getpass
import typing

from . import cache_io, surveys_io, auth

__all__ = ['add_user', 'remove_user', 'remove_all_users']


def add_user() -> None:
    username, password = collect_pavlovia_login_details()
    token = auth.get_pavlovia_access_token(username, password)
    cache_io.add_user_to_cache(username, token)
    print("--Added user: ", username)


def list_users() -> typing.List:
    return cache_io.load_available_users()


def remove_user(user) -> None:
    cache_io.remove_user_from_cache(user)
    print("--Removed user: ", user)


def remove_all_users() -> None:
    while True:
        pick = input("This will delete all users data? Type [Y]es/[N]o \n> ")
        pick = pick.lower().strip()
        if pick == "yes" or pick == "y":
            cache_io.purge_cache()
            print("--Removed all users")
            break
        elif pick == "no" or pick == "n":
            break
        else:
            print("Please input Yes/No.")


def list_surveys(user) -> None:
    return surveys_io.get_available_surveys_details(cache_io.load_token_for_user(user))

def get_surveys(user, surveys) -> None:
    token = cache_io.load_token_for_user(user)

    if isinstance(surveys, str):
        surveys = [surveys]

    return surveys.get_surveys(cache_io.load_token_for_user(user))


def collect_pavlovia_login_details() -> typing.Tuple:
    user_name = input("Enter email or username: ")
    password = getpass.getpass("Enter your password: ")
    return user_name, password
