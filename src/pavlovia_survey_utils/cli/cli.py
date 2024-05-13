import typing

import click

from ..api import auth, survey_utils

__all__ = ['list_users', 'add_user', 'update_user',
           'remove_user', 'remove_all_users',
           'list_surveys']

def _pretty_print_collection(collection: typing.Collection) -> None:
    click.echo("\n".join([f"* {item}" for item in collection]))


@click.group()
def main():
    click.echo('Pavlovia Survey Utils CLI (v0.1.0). ')


@main.command()
def list_users():
    """List all users."""
    res = auth.load_available_users()
    # Start with a newline and * for each user.
    click.echo("\n".join([f"* {user}" for user in res]))


@main.command()
def add_user():
    """Add a user."""
    username, password = collect_pavlovia_login_details()
    if username in auth.load_available_users():
        click.echo("User already exists. Use update-user to update the user.")
        click.echo("Operation cancelled.")
    else:
        auth.add_user_to_cache(username, password)
        click.echo(f"--Added user: {username}")


@main.command()
def update_user():
    """Update a user."""
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


@main.command()
@click.argument('user')
def remove_user(user):
    """Remove a user."""
    if user not in auth.load_available_users():
        click.echo(f"User {user} not found.")
        return
    else:
        if click.confirm(f'This will delete the user ({user}). Are you sure?'):
            click.echo(auth.remove_user_from_cache(user))
        else:
            click.echo("Operation cancelled.")


@main.command()
def remove_all_users():
    if click.confirm('This will delete all users data? Type [Y]es/[N]o'):
        auth.purge_cache()
        click.echo("--Removed all users")
    else:
        click.echo("Operation cancelled.")


@main.command()
@click.argument('user')  # , help='Full pavlovia username (email).')
@click.option('--access_rights', default='both')  # , help='owned or shared (default both).')
def list_surveys(user, access_rights='both'):
    """List all surveys for a user."""
    click.echo(survey_utils.load_available_surveys(auth.load_token_for_user(user)))


@main.command()
@click.argument('user')  # , help='Full pavlovia username (email).')
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
    username = click.prompt("Enter email or username")
    password = click.prompt("Enter password", hide_input=True)
    return username, password


main.add_command(list_surveys)
main.add_command(add_user)
main.add_command(update_user)
main.add_command(list_users)
main.add_command(remove_user)
main.add_command(remove_all_users)
main.add_command(get_surveys)

if __name__ == '__main__':
    main()
