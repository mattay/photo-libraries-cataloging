# from typing import list

from photologue.catalogue import Catalogue
from photologue.clean import Clean
from photologue.files import clean_name, library

import logging
import re
# from pprint import pprint


class Images:
    def __init__(self, indexing_cabinate, raw_extentions, cleanup):
        self.LOGGER = logging.getLogger('Images')
        self.CATALOGUE = Catalogue(indexing_cabinate)
        self.CLEAN = Clean(cleanup['preferred'], cleanup['ignore'], cleanup['camera_rules'])
        self.raw_extentions = raw_extentions

    def __list(self) -> list[str]:
        images = self.CATALOGUE.images()
        return images

    def image_files(self, image: str) -> list[dict]:
        return self.CATALOGUE.image_files(image)

    def list_files(self) -> dict:
        return {
            i: self.files(i)
            for i
            in self.__list()
        }

    def list_catorgoried(self) -> dict:
        types: dict[str, list] = {
            'dsc': [],
            '_dsc': [],
            'imgp': [],
            'img_': [],
            'gopr': [],
            'p': [],
            'igp': [],
            'other': []
        }

        for image in self.__list():
            dsc = re.match(r'^DSC\d{5}', image) 		# DSC00857
            _dsc = re.match(r'^_DSC\d{4}', image)		# _DSC1990
            imgp = re.match(r'^IMGP\d{4}', image)		# IMGP0001
            img_ = re.match(r'^IMG_\d{4}', image)		# IMG_1890
            gopr = re.match(r'^GOPR\d{4}', image)		# GOPR0023
            p = re.match(r'^P\d{7}', image)					# P1000920
            igp = re.match(r'^_IGP\d{4}', image)		# _IGP0014

            if dsc:
                types['dsc'].append(image)
            elif _dsc:
                types['_dsc'].append(image)
            elif imgp:
                types['imgp'].append(image)
            elif img_:
                types['img_'].append(image)
            elif gopr:
                types['gopr'].append(image)
            elif p:
                types['p'].append(image)
            elif igp:
                types['igp'].append(image)
            else:
                types['other'].append(image)

        return types

    def files(self, missing: str = "") -> list:
        files = self.CATALOGUE.files(missing)
        return list(files)

    def add_file(self, image_path: str) -> str | None:
        """
        FIXME: Document what's going on here
        """
        lib = library(image_path)

        if lib['library_type'] is None or lib['is'] in ['is_master', 'is_original']:
            image = clean_name(image_path)

            if image['thumbnail'] or image['face']:
                pass  # Ignore

            else:
                image['raw_image'] = True if image['extention'] in self.raw_extentions else False
                self.CATALOGUE.add_file(image)
                self.CATALOGUE.add_library(image_path, lib)
                return image_path

        elif lib['is'] not in ['is_preview', 'is_thumbnail', 'is_proxy', 'is_resource']:
            pass  # Ignore

        return None

    def add_stats(self, image_path: str, filestats: dict) -> None:
        self.CATALOGUE.add_filestats(image_path, filestats)

    def add_checksum(self, image_path: str, checksum: str) -> None:
        self.CATALOGUE.add_checksum(image_path, checksum)

    def add_exif(self, image_path: str, exif: dict) -> None:
        self.CATALOGUE.add_exif(image_path, exif)

    def save(self) -> None:
        self.CATALOGUE.save()

    def cameras(self) -> dict:
        self.CLEAN.add_camera_models(self.CATALOGUE.cameras())

        return self.CLEAN.rules()

    def process_images(self) -> None:
        for camera in self.CATALOGUE.cameras():
            self.CLEAN.add_camera_models(self.CATALOGUE.cameras())
            self.CLEAN.process_camera_images(camera, self.CATALOGUE.camera_files(camera))
