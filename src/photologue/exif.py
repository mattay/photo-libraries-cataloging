# Code initialy sourced from
# https://github.com/daviss92/py3meta/blob/master/py3exif.py

# import os
# import re
# import sys
import logging
import pathlib
import platform
# from pprint import pprint
import subprocess

_read_formats = ["JPG", "PEF", "DNG", "RW2", "JPEG"]

# import exiftool
# TiffImagePlugin = False
# desired_metadata = [
#     'Model',
#     'DateTime',
#     'DateTimeDigitized',
#     'DateTimeOriginal'
# ]


def _verify_installation(path):
    pctype = platform.system()

    if path is None:
        if (pctype.lower() == "darwin" or "linux" in pctype.lower()):
            cmd = "exiftool"
        else:
            cmd = "exiftool.exe"
    else:
        if (pctype.lower() == "darwin" or "linux" in pctype.lower()):
            if (pathlib.Path(path).is_file() or path == "exiftool"):
                cmd = path
            else:
                cmd = "exiftool"
        else:
            if (pathlib.Path(path).is_file() or "exiftool.exe" in path):
                cmd = path
            else:
                cmd = "exiftool.exe"

    try:
        results = _run_command(cmd)
    except Exception as e:
        print(e)
        raise RuntimeError("Running this requires exiftool installed.")
    else:
        if any(a in str(results) for a in ["command not found", "is not recognized"]):
            raise RuntimeError("Running this requires exiftool installed.")

    return cmd


def _verify_file(c, f):
    if not pathlib.Path(f).is_file():
        return ("{} is not a valid file.").format(f)

    if not any(pathlib.Path(f).suffix[1:].upper() in x for x in _read_formats):
        return ("{} is not a valid file type to {}.").format(f, c)

    try:
        fp = open(f)
        fp.close()
        return True
    except IOError as e:
        return (f"You do not have permissions to {c} the file {f}. - {e}")


def _cleanup_data(filepath, data):
    asList = [s
              for s
              in data.split("\n")
              if s != ''
              ]

    ignore = [
        'Create Date                     :     :  :     :  :',
        'Date/Time Original              :     :  :     :  :'
    ]

    cleaned = {}
    # to dict
    for s in asList:
        if ' : ' in s:
            items = s.split(' : ')
            if len(items) == 2:
                k, v = items
                k = k.strip()
                cleaned[k] = v.strip()

            elif s not in ignore:
                print(filepath)
                print(f'--> many occurances of " : " found in "{s}"')

        else:
            # TODO: handle when no space before :
            # print('-->', s)
            pass

    return cleaned


def _run_command(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output, err = proc.communicate()
    proc.wait()

    return str(output, 'UTF-8', 'ignore')


class Exif(object):

    def __init__(self, path=None):
        self.LOGGER = logging.getLogger('EXIF')
        self.exiftool = _verify_installation(path)

    def all_data(self, filepath, datatype="string"):
        valid = _verify_file("read", filepath)

        if valid is True:
            cmd = '"{}" "{}"'.format(self.exiftool, filepath)
            results = _run_command(cmd)
            data = _cleanup_data(filepath, results)
        else:
            self.LOGGER.warning(valid)
            return valid

        return data
