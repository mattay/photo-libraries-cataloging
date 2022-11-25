#!/usr/bin/env python3
""" Catalogue - Creates a Catalogue of image files to identify master versions

Usage:
		main.py collect (checksums|exifs|files|stats)
		main.py missing (checksums|exifs|stats) [--print0]
		main.py mappings [--verbose]
		main.py rules
		main.py (-h | --help)
		main.py --version
		main.py --verbose

Options:
		-h --help			 Show this screen.
		--version			 Show version.
		--verbose			 Print more text
		--sample
		--collectstats
		--filesearch
"""
from docopt import docopt
# from configparser import ConfigParser
import os
import sys
from pprint import pprint
from datetime import datetime
import re

# File readers
import logging
from logging.config import fileConfig
import yaml

# Progress bar
import alive_progress

# Application libs
from src.images import Images


# Global access to libraries as a shared datasource
# LOGGER = None
# CONFIG = None
# IMAGES = None

ABOUT = {
	'__version__': '0.0.0',
	'command': None,
	'mode': None
}

PATHS = {
		'config': 'configuration/config.yml',
		'logging': 'configuration/logging.ini',
		'mapping': 'reports'
}

def setup() -> None:
		global LOGGER, CONFIG, IMAGES

		config_yml=PATHS['config']
		logger_ini=PATHS['logging']

		# Logging
		if not os.path.exists(logger_ini):
			print(f'Logging config file does not exist: {logger_ini}')
			exit()
		else:
			date = datetime.now().strftime('%Y:%m:%d_%H:%M:%S')
			command = f"{ABOUT['command']}"
			if ABOUT['mode']:
				command = f"{command}__{ABOUT['mode']}"

			fileConfig(logger_ini, defaults={'date':date, 'command':command})
			LOGGER = logging.getLogger()
			LOGGER.info(f"Version: {ABOUT['__version__']}")
			LOGGER.info(f"Command: {command}")

		# Configuration
		if not os.path.exists(config_yml):
				LOGGER.error(f'Config file does not exist: {config_yml}')
				exit()
		else:
			with open(config_yml, "r") as yamlfile:
				CONFIG = yaml.load(yamlfile, Loader=yaml.FullLoader)
				LOGGER.info(f'Loading configuration file successful - {config_yml} ')

		# Check config for expected values
		for v in ['indexing_cabinate', 'import', 'cleanup', 'raw_extentions']:
			config_okay = True
			if v not in CONFIG:
				config_okay = False
				LOGGER.error(f'Missing config property {v}')
			
			if not config_okay:
				LOGGER.error(f'EXITING - Configuration file missing properties!')
				exit()

		# Progress Bar
		alive_progress.config_handler.set_global(title_length=48)

		# Images class
		IMAGES = Images(
			CONFIG.get('indexing_cabinate'), 
			CONFIG.get('import').get('raw_extentions'),
			CONFIG.get('cleanup')
		)
		

def collect(mode: str) -> None:
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
					'mtime':incoming.group('modified'),
					'atime':incoming.group('accessed')
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

	print (f'{counter} {mode}')


def clean_exif(file) -> dict:
		cleaned = {}
		for tag, value in file.groupdict().items():
			if tag == 'camera_make' and value == '-':
				value = 'unknown'
			if tag == 'camera_model' and value == '-':
				value = 'unknown'

			cleaned[tag] = None if value == '-' else value
			
		return cleaned


def missing (mode: str, line_ending: str="\n") -> None:
	for file in IMAGES.files(mode):
		sys.stdout.write(f"{file}{line_ending}")


def rules() -> None:
		LOGGER.info(f'Processing Rules')
		IMAGES.process_images()


def mapping() -> None:
		# 	pprint('Mappings')
		# mappings = Mappings()
		# mappings.add_images(IMAGES.list_files())
	
		# mappings.report(PATHS['mapping'])

	# 	#  TODO: list of images
	# 	#  each file ->
	# 	#  -- library or path
	# 	#  -- camera model
	# 	#  -- file format
	# 	#  -- original date
	pass

def handle_cmd(arguments) -> None:
	global IMAGES, CONFIG

	mode = ABOUT['mode']
	command = ABOUT['command']

	if command == 'collect':
		collect(mode)

	if command == 'missing':
		line_ending = "\x00" if arguments['--print0'] else "\n"
		missing(mode, line_ending)

	if command == 'rules':
		rules()

	# if command == 'mappings':
	# 	mapping()

def pick_args(arguments: dict={}, valid_options: list=[]) -> str|None:
	for arg in arguments.keys():
		if arguments[arg] and arg in valid_options:
			return arg
	
	return None

#
# ==> Entry Point
#
def main():
	# Fetch versioning
	here = os.path.abspath(os.path.dirname(__file__))
	version = {}
	with open(os.path.join(here, 'src', '__version__.py')) as f:
		exec(f.read(), version)
	ABOUT['__version__'] = version['__version__']

	# Handle args thanks to DocOpt
	arguments = docopt(__doc__, version=ABOUT['__version__'])
	
	ABOUT['verbose'] = arguments['--verbose']
	ABOUT['command'] = pick_args(arguments, ['collect', 'missing', 'rules'])
	ABOUT['mode'] = pick_args(arguments, ['files', 'exifs', 'stats', 'checksums'])	

	setup()
	
	handle_cmd(arguments)

if __name__ == '__main__':
	main()