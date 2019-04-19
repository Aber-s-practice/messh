#!/usr/bin/python3
import os
import sys
import json
import getpass
import argparse


try:
    import colorama
except ImportError:
    print("Auto install `colorama` by `pip3`")
    os.system("sudo pip3 install colorama")
    import colorama


def create_ssh_connection(config: dict):
    cmd = f"sshpass -p {config['pass']} ssh {config['user']}@{config['host']} -o StrictHostKeyChecking=no"
    if config.get("port"):
        cmd += f" -p {config['port']}"
    os.system(cmd)


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
            print(f"- [{i}] {colorama.Fore.GREEN}{item['user']}@{item['host']:<16}", end=" ")
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

    def update(self, item: dict):
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
    elif args.e is not None:
        item = config.data[args.e]
        item['name'] = input(f"input new name for{item['user']}@{item['host']}")
        config.update(item)
        return

    try:
        index = int(args.t)
        item = config.data[index]
    except TypeError:
        parser.print_help()
        return
    except IndexError:
        print(colorama.Fore.RED+"Over index!")
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
            config.update(item)
        except IndexError:
            print(colorama.Fore.RED+"Must input target(-t) like: user@host or index of config")
            return
    return item


def main():
    config = create_conf()
    parser = argparse.ArgumentParser(description='manager your ssh config')
    parser.add_argument('-t', metavar='target', type=str, help='like `root@host` or index of config')
    parser.add_argument('-p', metavar='port', type=int, help='port, an integer, default 22', default=22)
    parser.add_argument('-e', metavar='edit', type=int, help='edit ssh config name with index')
    parser.add_argument('-n', metavar='name', help="host nickname will display", default="")
    parser.add_argument("-l", help='display all ssh config without password', action="store_true")
    parser.add_argument("-d", metavar='delete', type=int, help='delete ssh config with index')
    args = parser.parse_args()
    item = get_config(args)
    if item is not None:
        create_ssh_connection(item)


if __name__ == "__main__":
    colorama.init(True)
    main()
