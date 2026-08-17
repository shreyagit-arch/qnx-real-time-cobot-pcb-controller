import json
import os


CONFIG_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "config",
    "experiment_config.json"
)


def load_config():
    with open(CONFIG_PATH, "r") as file:
        return json.load(file)