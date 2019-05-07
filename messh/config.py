import os
import json

import colorama


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
