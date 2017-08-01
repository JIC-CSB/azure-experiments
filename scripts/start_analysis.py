"""Determine work and load queue."""

import json

import click
import redis

from dbluesea import AzureDataSet


def identifiers_where_overlay_is_true(dataset, overlay_name):

    overlay = dataset.access_overlay(overlay_name)

    selected = [identifier
                for identifier in dataset.identifiers
                if overlay[identifier]]

    return selected


def make_task(input_uuid, identifier, output_uuid):
    task = {
        "tool_path": "python /home/hartleym/bt2align/scripts/bt2align.py",
        "input_uuid": input_uuid,
        "identifier": identifier,
        "output_uuid": output_uuid,
    }

    return json.dumps(task)


@click.command()
@click.argument('input_uuid')
@click.argument('output_uuid')
def main(input_uuid, output_uuid):
    r = redis.StrictRedis(host='10.0.0.4', port=6379)

    dataset = AzureDataSet.from_uuid(input_uuid)

    for i in identifiers_where_overlay_is_true(dataset, 'is_read1'):
        task = make_task(input_uuid, i, output_uuid)
        r.lpush('tasks', task)


if __name__ == '__main__':
    main()
