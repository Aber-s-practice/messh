import os
import sys
import json
import getpass
import argparse

import colorama
import click

from .config import FileConfig, create_conf
from .ssh import create_ssh_connection


config = create_conf()


@click.group()
def main():
    pass


def show_list():
    for i, item in enumerate(config.data):
        print(f"- [{i}] {colorama.Fore.GREEN}{item['user']}@{item['host']:<16}", end=" ")
        print(f"{item['name']}")


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
def connect(target, port, name):
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
        click.secho(" Config list: ")
        show_list()
        sys.exit(1)
    # create ssh connection
    create_ssh_connection(item)


if __name__ == "__main__":
    main()
