import json
import time
import shlex
import subprocess

import click
import redis


def execute_task(task):

    command = shlex.split(task["tool_path"])
    command += ['-d', task["input_uuid"]]
    command += ['-i', task["identifier"]]
    command += ['-o', task["output_uuid"]]

    subprocess.call(command)


@click.command()
def main():
    r = redis.StrictRedis(host='10.0.0.4', port=6379)

    while True:
        _, raw_task = r.blpop('tasks')

        task = json.loads(raw_task)

        execute_task(task)


if __name__ == '__main__':
    main()
