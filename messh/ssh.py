import os

import colorama

colorama.init(autoreset=True)


def create_ssh_connection(config: dict):
    """create new ssh connection"""
    cmd = f"sshpass -p {config['pass']} ssh {config['user']}@{config['host']} -o StrictHostKeyChecking=no"
    if config.get("port"):
        cmd += f" -p {config['port']}"
    os.system(cmd)
