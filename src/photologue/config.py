#!/usr/bin/env python3
""" Catalogue - Exports list from config without loading database connection

Usage:
        config.py paths
        config.py extentions

"""
from typing import Any

import os

# File readers
import yaml
from docopt import docopt


# Global access to libraries as a shared datasource
CONFIG: Any
ABOUT = {
    '__version__': '0.0.1',
    'command': None,
    'mode': None
}


def setup() -> None:
    global CONFIG

    config_yml = os.environ.get('CONFIG_FILE_YML', 'config.yml')

    # Configuration
    if not os.path.exists(config_yml):
        print(f'Config file does not exist: {config_yml}')
        exit(1)
    else:
        with open(config_yml, "r") as yamlfile:
            CONFIG = yaml.load(yamlfile, Loader=yaml.FullLoader)

    # Check config for expected values
    for v in ['import']:
        config_okay = True
        if v not in CONFIG:
            config_okay = False
            print(f'Missing config property {v}')

        if not config_okay:
            print(f'EXITING - Configuration file missing properties! - {config_yml}')
            exit(1)


def pick_args(arguments: dict = {}, valid_options: list = []) -> str | None:
    for arg in arguments.keys():
        if arguments[arg] and arg in valid_options:
            return arg

    return None


def main():
    global CONFIG

    # Handle args thanks to DocOpt
    arguments = docopt(__doc__, version=ABOUT['__version__'])
    # pprint(arguments)

    ABOUT['verbose'] = arguments['--verbose']
    ABOUT['command'] = pick_args(arguments, ['collect', 'missing', 'rules'])

    setup()

    command = ABOUT['command']

    if command == 'paths':
        if 'volumes' not in CONFIG['import']:
            print('EXITING - Configuration file missing properties! - "volumes" in "import"')
            exit(1)

        print('\n'.join([
            path
            for volPaths
            in CONFIG['import']['volumes'].values()
            for path
            in volPaths])
        )

    if command == 'extentions':
        if 'extentions' not in CONFIG['import']:
            print('EXITING - Configuration file missing properties! - "extentions" in "import"')
            exit(1)

        print('\n'.join([
            extention
            for extention
            in CONFIG['import']['extentions']
        ]))


if __name__ == '__main__':
    main()
