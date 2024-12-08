import os

import jsonlines
import yaml


def read_yaml(filename):
    with open(filename, "r") as f:
        return yaml.safe_load(f)


def save_jsonl(data, filename):
    base_dir = os.path.dirname(filename)
    os.makedirs(base_dir, exist_ok=True)

    with jsonlines.open(filename, "w") as writer:
        writer.write_all(data)


def read_jsonl(filename):
    with jsonlines.open(filename) as reader:
        for obj in reader:
            yield obj
