import getpass
import typing

import click

from ..api import auth, survey_utils


@click.group()
def main():
    """Welcome to pavlovia_survey_utils! [Version {}]"""
    pass


@click.command()
def greet():
    click.echo('Type "help" to see available commands.')
    click.echo('Type "exit" to quit the program.')


@click.command()
def add_user():
    """Add a user."""
    username, password = collect_pavlovia_login_details()
    token = auth.get_pavlovia_access_token(username, password)
    auth.add_user_to_cache(username, token)
    click.echo("--Added user: ", username)


@click.command()
def update_user():
    """Update a user."""
    username, password = collect_pavlovia_login_details()
    # Does the user already exist?
    if username in auth.load_available_users():
        click.echo("User already exists. Updating user.")
    else:
        click.echo("User does not exist. Adding user.")
    token = auth.get_pavlovia_access_token(username, password)
    auth.add_user_to_cache(username, token)
    click.echo("--Added user: ", username)


@click.command()
def list_users():
    """List all users."""
    click.echo(auth.load_available_users())


@click.confirm('This will delete the user stored data. Are you sure?')
@click.command()
@click.argument('user')
def remove_user(user):
    """Remove a user."""
    click.echo(auth.remove_user_from_cache(user))


@click.command()
@click.confirm('This will delete all users data? Type [Y]es/[N]o')
def remove_all_users():
    auth.purge_cache()
    click.echo("--Removed all users")


@click.command()
@click.argument('user', help='Full pavlovia username (email).')
@click.option('--access_rights', default='both', help='owned or shared (default both).')
def list_surveys(user, access_rights='both'):
    """List all surveys for a user."""
    click.echo(survey_utils.load_available_surveys(auth.load_token_for_user(user)))


@click.command()
@click.argument('user', help='Full pavlovia username (email).')
@click.option('surveys', '--surveys',
                help='Single survey id or a list of survey ids, separated by a colon (:) on Linux and Mac, and a semicolon (;) on Windows.',
                multiple=True,
                type=click.Tuple([str, typing.List[str]]))
@click.option('path', '--path', help='Path to save the surveys.', default='.')
def get_surveys(user, surveys, path):
    """Get all available surveys for a user.

    The returned value is a dictionary with the survey id as the key and the survey name as the value.


    param user: Full pavlovia username (email).
    param surveys: Single survey id or a list of survey ids, separated by a colon (:) on Linux and Mac, and a
        semicolon (;) on Windows. If not provided, all surveys will be returned.

    return: dict: A dictionary with the survey id as the key and the survey name as the value.

    exmple:
    >>> survey-utils get-surveys foo --surveys 12-13 : 14-15 --path /home/user/surveys
    """
    token = auth.load_token_for_user(user)

    if isinstance(surveys, str):
        surveys = [surveys]

    click.echo(survey_utils.download_surveys(token, surveys, path))


def collect_pavlovia_login_details() -> typing.Tuple:
    user_name = click.prompt("Enter email or username")
    password = getpass.getpass("Enter your password")
    return user_name, password


# main.add_command(greet)
# main.add_command(add_user)
# main.add_command(update_user)
# main.add_command(list_users)
# main.add_command(remove_user)
# main.add_command(remove_all_users)
# main.add_command(list_surveys)
# main.add_command(get_surveys)

if __name__ == '__main__':
    main()
