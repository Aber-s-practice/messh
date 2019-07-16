import os
import re
import sys
import json
import getpass
import argparse

import colorama
import pysftp
import click

from .config import FileConfig, create_conf
from .ssh import create_ssh_connection, execute_by_ssh_connection


config = create_conf()


@click.group()
def main():
    pass


def show_list():
    print("Configuration list")
    if config.data:
        for i, item in enumerate(config.data):
            print("- ", end="")
            print(f"[{i}] {colorama.Fore.GREEN}{item['user']}@{item['host']:<16}", end=" ")
            print(f"{item['name']}")
    else:
        print("  ", end="")
        print(colorama.Fore.BLUE+"Empty list")
    print()


@main.command(name="list", help="display all ssh configurations")
def display():
    show_list()


@main.command(help="delete a ssh configuration")
@click.argument('index', type=int)
def delete(index):
    config.delete(index)


@main.command(help="edit nickname for a ssh configuration")
@click.argument('index', type=int)
def edit(index):
    item = config.data[index]
    click.secho("input new name for", nl=False)
    click.secho(f" {item['user']}@{item['host']}", nl=False, fg='green')
    click.secho(" : ", nl=False)
    name = input()
    if name:  # if not a emtpy string
        item['name'] = name
    config.update(item)


def parse_target(target, port, name, password, dont_create):
    try:
        target = int(target)
        item = config.data[target]
    except ValueError:
        try:
            target = target.split("@")
            assert len(target) == 2
            if password is None:
                password = getpass.getpass()
            item = {
                'user': target[0],
                'host': target[1],
                'port': port,
                'name': name,
                'pass': password,
            }
            if not dont_create:
                config.update(item)
        except AssertionError:
            click.secho("Must input target like: user@host or index of config", fg='red')
            sys.exit(1)
    except IndexError:
        click.secho("Over index!", fg='red', nl=False)
        show_list()
        sys.exit(1)
    return item


@main.command(help="connect target host by ssh")
@click.argument('target')
@click.option('--port', metavar='port', type=int, help='port, an integer, default 22', default=22)
@click.option('--name', metavar='name', help="host nickname will display", default="")
@click.option('--password', metavar='password', default=None)
@click.option('--only-create', ' / --no-only-create', metavar='only-create', help="only update a ssh config without connect", default=False)
@click.option('--dont-create', ' / --no-dont-create', metavar='dont-create', help="only connect without update config", default=False)
def connect(target, port, name, password, only_create, dont_create):
    if only_create and dont_create:
        click.secho("You can't use --only-create and --dont-create together!", fg='red', nl=False)
        sys.exit(1)
    item = parse_target(target, port, name, password, dont_create)
    # create ssh connection
    if not only_create:
        create_ssh_connection(item)


@main.command(help="execute command by ssh")
@click.argument('target')
@click.argument('command')
@click.option('--port', metavar='port', type=int, help='port, an integer, default 22', default=22)
@click.option('--name', metavar='name', help="host nickname will display", default="")
@click.option('--password', metavar='password', default=None)
@click.option('--dont-create', ' / --no-dont-create', metavar='dont-create', help="only execute without update config", default=False)
def execute(target, command, port, dont_create):
    item = parse_target(target, port, name, dont_create)
    click.secho("Execute command: ", nl=False)
    click.secho(command, fg='blue')
    execute_by_ssh_connection(item, command)


def is_ignore(path: str, ignore: list, local: str) -> bool:
    path = path.replace("\\", "/")

    for _ignore in ignore:
        _ignore = _ignore.replace("\\", "/")
        if _ignore.startswith("./") or _ignore.startswith("/"):
            if path == os.path.join(local, ignore).replace("\\", "/"):
                return True
        elif re.search("\*\.(.*)", _ignore):
            if path.endswith(_ignore.split("*")[1]):
                return True
        else:
            if _ignore in path:
                return True
    return False


@main.command(help="Upload all file from local to remote")
@click.argument('target')
@click.option('--port', metavar='port', type=int, help='port, an integer, default 22', default=22)
@click.option('--name', metavar='name', help="host nickname will display", default="")
@click.option('--password', metavar='password', default=None)
@click.option('-l', '--local', default=os.getcwd(), help='default os.getcwd()')
@click.option('-r', '--remote', required=True)
@click.option('--ignore', multiple=True)
@click.option('--dont-create', ' / --no-dont-create', metavar='dont-create', help="only upload without update config", default=False)
def upload(local, remote, target, port, password, name, ignore, dont_create):
    item = parse_target(target, port, name, password, dont_create)

    click.secho(f"Upload all file in ", nl=False)
    click.secho(local, fg="blue", nl=False)
    click.secho(" to ", nl=False)
    click.secho(f"{item['host']}:{remote}", fg="blue")

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(
        host=item["host"],
        port=item["port"],
        username=item["user"],
        password=item["pass"],
        cnopts=cnopts
    ) as sftp:  # pysftp.Connection
        if not sftp.exists(remote):
            sftp.makedirs(remote)
        sftp.chdir(remote)

        for root, directories, files in os.walk(local):
            root = os.path.relpath(root, local).replace("\\", "/")

            for directory in directories:
                directory = os.path.join(root, directory).replace("\\", "/")

                if is_ignore(directory, ignore, local):
                    continue

                if not sftp.exists(directory):
                    sftp.mkdir(directory)

            for file in files:
                file = os.path.join(root, file).replace("\\", "/")

                if is_ignore(file, ignore, local):
                    continue

                sftp.put(os.path.join(local, file), file)


if __name__ == "__main__":
    main()
