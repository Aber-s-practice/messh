import os
import sys
import time
import threading

import colorama
import paramiko

colorama.init(autoreset=True)


def create_ssh_connection(config: dict):
    """create new ssh connection"""
    cmd = f"sshpass -p {config['pass']} ssh {config['user']}@{config['host']} -o StrictHostKeyChecking=no"
    if config.get("port"):
        cmd += f" -p {config['port']}"
    os.system(cmd)


def execute_by_ssh_connection(config: dict, command: str):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(config['host'], port=config['port'], username=config['user'], password=config['pass'], compress=True)
    stdin, stdout, stderr = client.exec_command(command)

    def stdout_bind():
        for each in stdout:
            sys.stdout.write(each)

    def stderr_bind():
        for each in stderr:
            sys.stderr.write(each)

    stdout_thread = threading.Thread(target=stdout_bind, daemon=True)
    stderr_thread = threading.Thread(target=stderr_bind, daemon=True)

    stdout_thread.start()
    stderr_thread.start()

    stdout_thread.join()
    stderr_thread.join()

    client.close()
