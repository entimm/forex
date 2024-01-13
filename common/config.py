import yaml

config = {}


def load_config():
    global config
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)


load_config()
