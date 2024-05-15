import click

from . import commands

@click.group()
def main():
    click.echo('Pavlovia Survey Utils CLI (v0.1.0). ')


main.add_command(commands.list_surveys)
main.add_command(commands.add_user)
main.add_command(commands.update_user)
main.add_command(commands.list_users)
main.add_command(commands.remove_user)
main.add_command(commands.remove_all_users)
main.add_command(commands.get_surveys)

if __name__ == '__main__':
    main()
