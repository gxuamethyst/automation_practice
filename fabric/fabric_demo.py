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

# schema: ip/host, user, password
TARGET_HOSTS = [
    # fake data.
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

    # use param '-o StrictHostKeyChecking=no' and '-o UserKnownHostsFile=/dev/null',
    # avoid of '/usr/bin/ssh-copy-id: ERROR: Host key verification failed.'
    command = "ssh-copy-id -o {} -o {} -i {} {}@{}".format(
        "StrictHostKeyChecking=no",
        "UserKnownHostsFile=/dev/null",
        TARGET_SSH_PUBLIC_KEY,
        connection.user,
        connection.host
    )
    result = connection.local(command)
    if result.exited != 0:
        print(result)
        return result.exited

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
