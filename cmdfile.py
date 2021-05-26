import yaml
import sys
from checks import *

def get_config_from_yamlfile(filepath):
    if filepath == '-':
        return yaml.load(sys.stdin, Loader=yaml.FullLoader)

    with open(filepath, 'r') as yaml_file:
        return yaml.load(yaml_file, Loader=yaml.FullLoader)

def get_commands_from_config(c):
    commands = []
    def scan(x):
        if 'type' in x.keys():
            commands.append(x)
        else:
            for key in x:
                scan(x[key])
    scan(c)
    return commands
