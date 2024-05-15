import os
import typing

import click

from pavlovia_survey_utils.api import auth, survey_utils


@click.command()
def list_users():
    """List all users."""
    _pretty_print_collection(auth.load_available_users())


@click.option('--username', '-u', help='Pavlovia username (email).', type=str)
@click.option('--password', '-p', help='Pavlovia password.', type=str)
@click.command()
def add_user(username=None, password=None):
    """Add a user."""
    # TODO - enable to either interactively enter the username or pass it as an argument.

    if username is None or password is None:
        username, password = collect_pavlovia_login_details()

    if username in auth.load_available_users():
        click.echo("User already exists. Use update-user to update the user.")
        click.echo("Operation cancelled.")
    else:
        auth.add_user_to_cache(username, password)
        click.echo(f"--Added user: {username}")

@click.option('--username', '-u', help='Pavlovia username (email).', type=str)
@click.option('--password', '-p', help='Pavlovia password.', type=str)
@click.command()
def update_user(username=None, password=None):
    """Update a user's access token."""

    # TODO - enable to either interactively enter the username or pass it as an argument.
    if username is None or password is None:
        username, password = collect_pavlovia_login_details()

    # Does the user already exist?
    if username in auth.load_available_users():
        if click.confirm("This will overwrite the user data? Type [Y]es/[N]o"):
            auth.add_user_to_cache(username, password, force_update=True)
            click.echo(f"--Updated user: {username}")
        else:
            click.echo("Operation cancelled.")
    else:
        click.echo("User does not exist.")


@click.command()
@click.argument('user', type=str)
def remove_user(user):
    """Remove user's login details."""
    if user not in auth.load_available_users():
        click.echo(f"User {user} not found.")
        return
    else:
        if click.confirm(f'This will delete the user ({user}). Are you sure?'):
            click.echo(auth.remove_user_from_cache(user))
        else:
            click.echo("Operation cancelled.")


@click.command()
def remove_all_users():
    """Remove all users."""
    if click.confirm('This will delete all users data? Type [Y]es/[N]o'):
        auth.purge_cache()
        click.echo("--Removed all users")
    else:
        click.echo("Operation cancelled.")


@click.command()
@click.argument('user')  # , help='Full pavlovia username (email).')
@click.option('--access_rights', default='both', show_default=True,
              type=click.Choice(['owned', 'shared', 'both']))
def list_surveys(user, access_rights='both'):
    """List all surveys for a user.

    param user: Full pavlovia username (email).
    """
    _pretty_print_collection(survey_utils.load_available_surveys(auth.load_token_for_user(user), access_rights))


@click.command()
@click.argument('user')  # , help='Full pavlovia username (email).')
@click.option('--surveys', '-s',
              help='Single survey id or a list of survey ids, separated by a colon (:) on Linux and Mac, and a semicolon (;) on Windows.',
              multiple=False,
              type=str)  # click.Tuple([str, typing.List[str]]))
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
        surveys = surveys.split(':' if os.name != 'nt' else ';')

    click.echo(survey_utils.download_surveys(token, surveys, path))


def collect_pavlovia_login_details() -> typing.Tuple:
    """Collect Pavlovia login details.

    :return: Tuple of username and password.
    """
    username = click.prompt("Enter email or username")
    password = click.prompt("Enter password", hide_input=True)
    return username, password


def _pretty_print_collection(collection: typing.Collection) -> None:
    """Pretty print a collection in a readable format."""
    # TODO - find a library to print this in a neat table format.
    if isinstance(collection, typing.Mapping):
        click.echo("\n".join([f"* {k} - {v}" for k, v in collection.items()]))
    else:
        click.echo("\n".join([f"* {item}" for item in collection]))
