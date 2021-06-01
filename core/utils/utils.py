import os
import json


###############################
# General
###############################


def read_json(path):
    """
    Read a json file
    """
    with open(path, 'r') as file:
        dic = json.loads(file.read())
    return dic


def write_json(dict, path):
    """
    Dump dict to a json file
    """
    with open(path, 'w') as file:
        json.dump(dict, file, indent=4, separators=(", ", ": "))


def listdir_nohidden(path: str):
    """
    List all non hidden files in path
    """
    new_list = []
    for f in os.listdir(path):
        if not f.startswith('.'):
            new_list.append(f)

    new_list.sort()

    return new_list
