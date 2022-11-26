#!/usr/bin/env python3
""" Catalogue - Creates a Catalogue of image files to identify master versions

Usage:
        config.py paths
        config.py extentions

"""
from docopt import docopt
import os
# from pprint import pprint

# File readers
import yaml

# Global access to libraries as a shared datasource
CONFIG = {}

PATHS = {
        'config': 'configuration/config.yml',
}

about = {
    '__version__': '0.0.0'
}


def setup(config_yml):
    global CONFIG

    # Configuration
    if not os.path.exists(config_yml):
            print(f'Config file does not exist: {config_yml}')
            exit()
    else:
        with open(config_yml, "r") as yamlfile:
            CONFIG = yaml.load(yamlfile, Loader=yaml.FullLoader)

    # Check config for expected values
    for v in ['indexing_cabinate', 'volumes', 'extentions']:
        config_okay = True
        if v not in CONFIG:
            config_okay = False
            print(f'Missing config property {v}')

        if not config_okay:
            exit()


def handle_cmd(arguments):

    if arguments['paths']:
        print('\n'.join([
            path
            for volPaths
            in CONFIG['import']['volumes'].values()
            for path
            in volPaths])
        )

    if arguments['extentions']:
        print('\n'.join([
            extention
            for extention
            in CONFIG['import']['extentions']
        ]))


def main():
    # Fetch versioning
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'src', '__version__.py')) as f:
        exec(f.read(), about)

    # Handle args thanks to DocOpt
    arguments = docopt(__doc__, version=about['__version__'])
    # pprint(arguments)

    # if arguments['--verbose']:
    # 	verbose = arguments['--verbose']
    # 	pprint(arguments)

    setup(PATHS['config'])

    handle_cmd(arguments)


if __name__ == '__main__':
    main()
