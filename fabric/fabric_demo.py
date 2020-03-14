#!/usr/bin/python3
# -*- coding: utf-8 -*-

from os import path

from fabric import (
    Connection,
    Config,
    ThreadingGroup
)
from invoke import UnexpectedExit

# Your SSH public key, will insert it into the remote host for authentication
TARGET_SSH_PUBLIC_KEY = "/Users/gxuamethyst/.ssh/id_rsa.pub"

TARGET_HOSTS = [
    # schema: ip/host, user, password
    ["192.168.1.2", "root", "f3Fk3sh8Et!c"],
    ["192.168.1.3", "root", "c#3Fk3sdisix"],
    ["192.168.1.4", "root", "sefdSX!]hBfz"]
]


def remote_run_command(connection: Connection, command: str):
    if connection is None or command is None:
        return None

    print("Running command '{}' on {}".format(command, connection.host))
    result = None
    try:
        result = connection.run(command, hide=True)
    except UnexpectedExit as e:
        print("Error while running '{}', message: {}".format(command, e))

    if result is not None:
        print("exited code: {}, stdout:\n{}".format(result.exited, result.stdout))

    return result


def insert_ssh_key_to_host(connection: Connection, ssh_key_file=None):
    if not path.exists(ssh_key_file):
        print("ssh key {} do not existed.".format(ssh_key_file))
        return -1

    # read ssh key file
    with open(ssh_key_file, "r") as key_file:
        ssh_key = key_file.read()

    # check if autoorized_keys file existed on remote host
    result = remote_run_command(connection, "ls ~/.ssh/authorized_keys")
    if result is not None:
        # check if ssh_key already inserted
        result = remote_run_command(connection, "cat ~/.ssh/authorized_keys")
        if ssh_key in result.stdout:
            print("ssh_key have already insert to {}, do nothing.".format(connection.host))
            return 0
        remote_run_command(connection, 'echo "' + ssh_key + '" >> ~/.ssh/authorized_keys')
    else:
        remote_run_command(connection, "mkdir -p ~/.ssh")
        remote_run_command(connection, "chmod 0700 ~/.ssh")
        remote_run_command(connection, 'echo "' + ssh_key + '" >> ~/.ssh/authorized_keys')
        remote_run_command(connection, "chmod 0600 ~/.ssh/authorized_keys")

    return 0


def serial_init():
    for host in TARGET_HOSTS:
        connection = Connection(
            host[0],
            user=host[1],
            connect_kwargs={
                "password": host[2],
            }
        )
        remote_run_command(connection, "ip a")
        insert_ssh_key_to_host(connection, TARGET_SSH_PUBLIC_KEY)


def parallel_job():
    hosts = []
    for host in TARGET_HOSTS:
        hosts.append(host[0])

    config = Config(overrides={
        "user": "root"
    })
    thread_group = ThreadingGroup(*hosts, config=config)
    thread_group.run('ip a')


if __name__ == "__main__":
    serial_init()
    parallel_job()
