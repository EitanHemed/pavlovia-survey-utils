import click
import getpass
import typing

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

@click.command()
@click.argument('user')
def remove_user(user):
    """Remove a user."""
    click.echo(auth.remove_user_from_cache(user))

@click.command()
def remove_all_users():
    """Remove all users."""
    while True:
        pick = click.prompt("This will delete all users data? Type [Y]es/[N]o")
        pick = pick.lower().strip()
        if pick == "yes" or pick == "y":
            auth.purge_cache()
            click.echo("--Removed all users")
            break
        elif pick == "no" or pick == "n":
            break
        else:
            click.echo("Please input Yes/No.")

@click.command()
@click.argument('user')
def list_surveys(user):
    """List all surveys for a user."""
    click.echo(survey_utils.load_available_surveys(auth.load_token_for_user(user)))

@click.command()
@click.argument('user')
@click.argument('surveys')
def get_surveys(user, surveys):
    """Get surveys for a user."""
    token = auth.load_token_for_user(user)

    if isinstance(surveys, str):
        surveys = [surveys]

    click.echo(surveys.get_surveys(auth.load_token_for_user(user)))

def collect_pavlovia_login_details() -> typing.Tuple:
    user_name = click.prompt("Enter email or username")
    password = getpass.getpass("Enter your password")
    return user_name, password

main.add_command(greet)
main.add_command(add_user)
main.add_command(update_user)
main.add_command(list_users)
main.add_command(remove_user)
main.add_command(remove_all_users)
main.add_command(list_surveys)
main.add_command(get_surveys)

if __name__ == '__main__':
    main()
