import os
import sys
import json
import getpass
import argparse

import colorama
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


@main.command(help="connect target host by ssh")
@click.argument('target')
@click.option('--port', metavar='port', type=int, help='port, an integer, default 22', default=22)
@click.option('--name', metavar='name', help="host nickname will display", default="")
@click.option('--only-create', ' /-O', metavar='only-create', help="only update a ssh config without connect", default=False)
def connect(target, port, name, only_create):
    try:
        target = int(target)
        item = config.data[target]
    except ValueError:
        try:
            target = target.split("@")
            assert len(target) == 2
            password = getpass.getpass()
            item = {
                'user': target[0],
                'host': target[1],
                'port': port,
                'name': name,
                'pass': password,
            }
            config.update(item)
        except AssertionError:
            click.secho("Must input target like: user@host or index of config", fg='red')
            sys.exit(1)
    except IndexError:
        click.secho("Over index!", fg='red', nl=False)
        show_list()
        sys.exit(1)
    # create ssh connection
    if not only_create:
        create_ssh_connection(item)


@main.command(help="execute command by ssh")
@click.argument('target')
@click.argument('command')
@click.option('--port', metavar='port', type=int, help='port, an integer, default 22', default=22)
def execute(target, command, port):
    try:
        target = int(target)
        item = config.data[target]
    except ValueError:
        try:
            target = target.split("@")
            assert len(target) == 2
            password = getpass.getpass()
            item = {
                'user': target[0],
                'host': target[1],
                'port': port,
                'pass': password,
            }
        except AssertionError:
            click.secho("Must input target like: user@host or index of config", fg='red')
            sys.exit(1)
    except IndexError:
        click.secho("Over index!", fg='red', nl=False)
        show_list()
        sys.exit(1)
    click.secho("Execute command: ", nl=False)
    click.secho(command, fg='blue')
    execute_by_ssh_connection(item, command)


if __name__ == "__main__":
    main()
