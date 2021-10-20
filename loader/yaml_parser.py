import yaml


def get_config():

    with open("../config.yaml", "r") as stream:

        yaml_storage = yaml.safe_load(stream)

    return yaml_storage
