#!/usr/bin/env python3
""" Catalogue - Creates a Catalogue of image files to identify master versions

Usage:
    main.py collect (checksums|exifs|files|stats)
    main.py missing (checksums|exifs|stats) [--print0]
    main.py mappings [--verbose]
    main.py rules
    main.py summary
    main.py (-h | --help)
    main.py --version
    main.py --verbose

Options:
    -h --help			  Show this screen.
    --version			  Show version.
    --verbose			  Print more text
    --sample
"""
from docopt import docopt
from typing import Any

import os
import sys
# from pprint import pprint
from datetime import datetime
import re

# File readers
from logging import Logger, getLogger
from logging.config import fileConfig
import yaml


# Application libs
from photologue.images import Images


# Global access to libraries as a shared datasource
VERSION = '0.5.1'
LOGGER: Logger
CONFIG: Any
IMAGES: Any
ABOUT = {
    '__version__': '0.5.2',
    'command': None,
    'mode': None
}


def setup() -> None:
    global LOGGER, CONFIG, IMAGES

    config_yml = os.environ.get('CONFIG_FILE_YML', 'config.yml')
    logger_ini = os.environ.get('LOGGING_CONFIG_INI', 'logging.ini')
    indexing_cabinate = os.environ.get('DATABASE_URL', 'catalogue/catalogue.db')

    # Logging
    if not os.path.exists(logger_ini):
        print(f'Logging config file does not exist: {logger_ini}')
        exit(1)
    else:
        path = os.environ.get('LOGGING_OUTPUT_PATH', 'logs').rstrip('/')
        date = datetime.now().strftime('%Y:%m:%d_%H:%M:%S')
        command = f"{ABOUT['command']}"
        mode = ABOUT['mode']
        if mode:
            command = f"{command}__{mode}"

        fileConfig(logger_ini, defaults={'path': path, 'date': date, 'command': command})
        LOGGER = getLogger()
        LOGGER.info(f"Version: {ABOUT['__version__']}")
        LOGGER.info(f"Command: {command}")
        LOGGER.info(f"Mode: {mode}")

    # Configuration
    if not os.path.exists(config_yml):
        LOGGER.error(f'Config file does not exist: {config_yml}')
        exit(1)
    else:
        with open(config_yml, "r") as yamlfile:
            CONFIG = yaml.load(yamlfile, Loader=yaml.FullLoader)
            LOGGER.info(f'Loading configuration file successful - {config_yml}')

    # Check config for expected values
    for v in ['import', 'cleanup', 'raw_extentions']:
        config_okay = True
        if v not in CONFIG:
            config_okay = False
            LOGGER.error(f'Missing config property {v}')

        if not config_okay:
            LOGGER.error(f'EXITING - Configuration file missing properties! - {config_yml}')
            exit(1)

    # Checking for database path
    if not indexing_cabinate:
        LOGGER.error('Enviroment variable not defined: "DATABASE_URL"')
        exit(1)

    # Images class
    IMAGES = Images(
        indexing_cabinate,
        CONFIG.get('import').get('raw_extentions'),
        CONFIG.get('cleanup')
    )


def collect(mode: str | None = None) -> None:
    global LOGGER
    counter = 0

    LOGGER.info(f'Collecting {mode}')
    for file in sys.stdin:
        #
        # Files
        #
        if mode == 'files':
            collected = IMAGES.add_file(file.rstrip('\n'))
            counter += 1 if collected else 0

        #
        # Stats
        #
        if mode == 'stats':
            incoming = re.match(r"^(?P<size>.+)\t(?P<birth>.+)\t(?P<change>.+)\t(?P<modified>.+)\t(?P<accessed>.+)\t(?P<file_path>.+)\n", file)
            if incoming:
                counter += 1
                IMAGES.add_stats(incoming.group('file_path'), {
                    'size': incoming.group('size'),
                    'birthtime': incoming.group('birth'),
                    'ctime': incoming.group('change'),
                    'mtime': incoming.group('modified'),
                    'atime': incoming.group('accessed')
                })
            else:
                LOGGER.warn(f'No stats found for {file}')

        #
        # EXIFs
        #
        if mode == 'exifs':
            incomingPattern = re.compile(r'''
        ^(?P<date_time_original>.+)
        \t(?P<date_time_modifed>.+)
        \t(?P<camera_make>.+)
        \t(?P<camera_model>.+)
        \t(?P<color_space>.+)
        \t(?P<x_resolution>.+)
        \t(?P<y_resolution>.+)
        \t(?P<resolution_unit>.+)
        \t(?P<quality>.+)
        \t(?P<image_height>.+)
        \t(?P<image_width>.+)
        \t(?P<software>.+)
        \t(?P<file_path>.+)
        \n
      ''', re.VERBOSE)
            incoming = incomingPattern.match(file)
            if incoming:
                counter += 1

                cleaned = clean_exif(incoming)
                IMAGES.add_exif(
                    cleaned['file_path'],
                    cleaned
                )
            else:
                LOGGER.warn(f'No exifs found for {file}')
        #
        # Checksums
        #
        if mode == 'checksums':
            incoming = re.match(r"^(?P<checksum>[0-9]+) (?P<octets>[0-9]+) (?P<file_path>.+)\n", file)
            if incoming:
                counter += 1
                IMAGES.add_checksum(incoming.group('file_path'), incoming.group('checksum'))

            else:
                LOGGER.warn(f'No checksums found for {file}')

    print(f'{counter} {mode}')


def clean_exif(file) -> dict:
    cleaned = {}
    for tag, value in file.groupdict().items():
        if tag == 'camera_make' and value == '-':
            value = 'unknown'
        if tag == 'camera_model' and value == '-':
            value = 'unknown'

        cleaned[tag] = None if value == '-' else value

    return cleaned


def missing(mode: str | None, line_ending: str = "\n") -> None:
    if mode:
        for file in IMAGES.files(mode):
            sys.stdout.write(f"{file}{line_ending}")


def rules() -> None:
    global LOGGER, IMAGES
    LOGGER.info('Processing Rules')
    IMAGES.process_images()


def mapping() -> None:
    # 	pprint('Mappings')
    # mappings = Mappings()
    # mappings.add_images(IMAGES.list_files())

    # mappings.report(PATHS['mapping'])

    #  TODO: list of images
    #  each file ->
    #  -- library or path
    #  -- camera model
    #  -- file format
    #  -- original date
    pass


def summary():
    global IMAGES
    total = 0

    image_types = IMAGES.list_catorgoried()
    for pattern, image_names in image_types.items():
        print(f'{pattern:>40} {len(image_names):>8,}')
        total += len(image_names)
    print(f'{"":=>40} {"":=>8}')
    print(f'{"TOTAL":>40} {total:>8,}')


def pick_args(arguments: dict = {}, valid_options: list = []) -> str | None:
    for arg in arguments.keys():
        if arguments[arg] and arg in valid_options:
            return arg

    return None

#
# ==> Entry Point
#


def main():
    global ABOUT

    # Handle args thanks to DocOpt
    arguments = docopt(__doc__, version=ABOUT['__version__'])  # type: ignore

    ABOUT['verbose'] = arguments['--verbose']
    ABOUT['command'] = pick_args(arguments, ['collect', 'missing', 'rules', 'summary'])
    ABOUT['mode'] = pick_args(arguments, ['files', 'exifs', 'stats', 'checksums'])

    setup()

    mode = ABOUT['mode']
    command = ABOUT['command']

    if command == 'collect':
        collect(mode)

    if command == 'missing':
        line_ending = "\x00" if arguments['--print0'] else "\n"
        missing(mode, line_ending)

    if command == 'rules':
        rules()

    if command == 'mappings':
        mapping()

    if command == 'summary':
        summary()


if __name__ == '__main__':
    main()
