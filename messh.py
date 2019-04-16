#!/usr/bin/python3
import os
import sys
import json
import getpass
import argparse


try:
    import paramiko
except ImportError:
    print("Auto install `paramiko` by `pip3`")
    os.system("sudo pip3 install paramiko")
    import paramiko

if __name__ == "__main__":
    try:
        import colorama
    except ImportError:
        print("Auto install `colorama` by `pip3`")
        os.system("sudo pip3 install colorama")
        import colorama
    colorama.init()


# Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>

# This file is part of paramiko.

# Paramiko is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.

# Paramiko is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.

# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.


import socket
import sys
from paramiko.py3compat import u

# windows does not have termios...
try:
    import termios
    import tty

    has_termios = True
except ImportError:
    has_termios = False


def interactive_shell(chan):
    if has_termios:
        posix_shell(chan)
    else:
        windows_shell(chan)


def posix_shell(chan):
    import select

    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        chan.settimeout(0.0)

        while True:
            r, w, e = select.select([chan, sys.stdin], [], [])
            if chan in r:
                try:
                    x = u(chan.recv(1024))
                    if len(x) == 0:
                        sys.stdout.write("\r\n*** EOF\r\n")
                        break
                    sys.stdout.write(x)
                    sys.stdout.flush()
                except socket.timeout:
                    pass
            if sys.stdin in r:
                x = sys.stdin.read(1)
                if len(x) == 0:
                    break
                chan.send(x)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)


# thanks to Mike Looijmans for this code
def windows_shell(chan):
    import threading

    sys.stdout.write(
        "Line-buffered terminal emulation. Press F6 or ^Z to send EOF.\r\n\r\n"
    )

    def writeall(sock):
        while True:
            data = sock.recv(256)
            if not data:
                sys.stdout.write("\r\n*** EOF ***\r\n\r\n")
                sys.stdout.flush()
                break
            sys.stdout.write(data.decode("UTF-8"))
            sys.stdout.flush()

    writer = threading.Thread(target=writeall, args=(chan,))
    writer.start()

    try:
        while True:
            d = sys.stdin.read(1)
            if not d:
                break
            chan.send(d)
    except EOFError:
        # user hit ^Z or F6
        pass


def create_ssh_connection(config: dict):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(config['host'], port=config['port'], username=config['user'], password=config['pass'], compress=True)
    channel = ssh.invoke_shell()
    interactive_shell(channel)
    channel.close()
    ssh.close()


class FileConfig:

    def __init__(self, path: str):
        self.__path = path
        self.__data = []
        self.load()
        assert isinstance(self.data, list)

    @property
    def data(self):
        return self.__data

    @property
    def path(self):
        return self.__path

    def display(self):
        for i, item in enumerate(self.data):
            print(f"- [{i}] {colorama.Fore.GREEN}{item['user']}@{item['host']:<16}{colorama.Fore.RESET}", end=" ")
            print(f"{item['name']}")

    def load(self):
        try:
            with open(self.path, "r") as file:
                self.__data = json.load(file)
        except FileNotFoundError:
            pass

    def save(self):
        with open(self.path, "w+") as file:
            json.dump(self.data, file, indent=4)

    def append(self, item: dict):
        assert item.get("user") is not None
        assert item.get("host") is not None
        assert item.get("pass") is not None
        for each in self.data:
            if item['user'] == each['user'] and item['host'] == each['host']:
                each.update(item)
                break
        else:
            self.__data.append(item)
        self.save()

    def delete(self, index: int):
        del self.data[index]
        self.save()


def create_conf():
    """create and return FileConfig object"""
    if os.name == "posix":
        root = "/etc"
    else:
        root = os.environ.get("windir", "C:")
    config = FileConfig(os.path.join(root, 'messh.conf'))
    return config


def get_config(args):
    config = create_conf()

    if args.l:
        config.display()
        return
    elif args.d is not None:
        config.delete(args.d)
        return
    try:
        index = int(args.t)
        item = config.data[index]
    except TypeError:
        parser.print_help()
        return
    except IndexError:
        print(colorama.Fore.RED+"Over index!"+colorama.Fore.RESET)
        return
    except ValueError:
        try:
            target = args.t.split("@")
            password = getpass.getpass()
            item = {
                'user': target[0],
                'host': target[1],
                'port': args.p,
                'name': args.n,
                'pass': password,
            }
            config.append(item)
        except IndexError:
            print(colorama.Fore.RED+"Must input target(-t) like: user@host or index of config"+colorama.Fore.RESET)
            return
    return item


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='manager your ssh config')
    parser.add_argument('-t', metavar='target', type=str, help='like `root@host` or index of config')
    parser.add_argument('-p', metavar='port', type=int, help='port, an integer, default 22', default=22)
    parser.add_argument('-n', metavar='name', help="host nickname will display", default="")
    parser.add_argument("-l", help='display all ssh config without password', action="store_true")
    parser.add_argument("-d", metavar='delete', type=int, help='delete ssh config with index')
    args = parser.parse_args()
    item = get_config(args)
    if item is not None:
        create_ssh_connection(item)
