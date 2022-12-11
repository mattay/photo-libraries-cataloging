# from typing import list

from photologue.catalogue import Catalogue
from photologue.clean import Clean
from photologue.files import clean_name, library

import logging
import re
from pprint import pprint


class Images:
    def __init__(
        self, indexing_cabinate: str,
        raw_extentions: list = [],
        cleanup: dict = {'preferred': {}, 'ignore': {}, 'camera_rules': {}}
    ):
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

    def list_catorgoried(self) -> dict[str, list]:

        types: dict[str, list] = {
            '########-####-####-####-############': [],
            '#_o': [],
            '*_n': [],
            '_**_*****': [],
            '_dsc****': [],
            '_igp****': [],
            'dsc*****': [],
            'formal*****': [],
            'gopr****': [],
            'img_****': [],
            'imgp****': [],
            'n*': [],
            'number': [],
            'p*******': [],
            '._*': [],
            'other': []
        }

        for image in self.__list():
            number = re.match(r'^\d+$', image)
            dsc = re.match(r'^DSC\d{5}', image) 		# DSC00857
            _dsc = re.match(r'^_DSC\d{4}', image)		# _DSC1990
            imgp = re.match(r'^IMGP\d{4}', image)		# IMGP0001
            img_ = re.match(r'^IMG_\d{4}', image)		# IMG_1890
            gopr = re.match(r'^GOPR\d{4}', image)		# GOPR0023
            p = re.match(r'^P\d{7}', image)	            # P1000920
            igp = re.match(r'^_IGP\d{4}', image)        # _IGP0014
            _n = re.match(r'^(\d+_)+n$', image)		    # 162617_10150095509069265_524009264_5821937_4498810_n
            _o = re.match(r'^(\w+_)+o$', image)		    # 243376_10150219436364265_524009264_6908391_1266382_o
            n = re.match(r'^n(\d+_)+\d+', image)        # n737368239_1619563_2369516
            _d = re.match(r'^_[\d_]\d_\d{5}', image)        # '_10_00030'
            # UID = re.match(r'^([A-Z0-9]+-)+([A-Z0-9]+)', image)  # '0BED3F79-451F-4452-83F0-030560A6DAD3',
            formal = re.match(r'^Formal\d{5}_jpg', image)  # Formal10014_jpg

            tmp_ = re.match(r'^\._', image)		# ._IMG_1890 .__IGP9999

            if number:
                types['number'].append(image)
            elif dsc:
                types['dsc*****'].append(image)
            elif _dsc:
                types['_dsc****'].append(image)
            elif imgp:
                types['imgp****'].append(image)
            elif img_:
                types['img_****'].append(image)
            elif gopr:
                types['gopr****'].append(image)
            elif p:
                types['p*******'].append(image)
            elif igp:
                types['_igp****'].append(image)
            elif _n:
                types['*_n'].append(image)
            elif _o:
                types['#_o'].append(image)
            elif n:
                types['n*'].append(image)
            elif _d:
                types['_**_*****'].append(image)
            # elif UID:
            #     types['########-####-####-####-############'].append(image)
            elif formal:
                types['formal*****'].append(image)
            elif tmp_:
                types['._*'].append(image)
            else:
                types['other'].append(image)
                print(image)

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

    def process_images(self) -> None:
        for camera in self.CATALOGUE.cameras():
            processed = self.CLEAN.process_camera_images(camera, self.CATALOGUE.camera_files(camera))
            for p in processed:
                if 'master' in p and p['master'] and len(p['copies']) >= 1:
                    for c in p['copies']:
                        self.CATALOGUE.add_relationship(c, 'copy', p['master'])
                elif p['momment'] and p['image']:
                    # print(p['master']) TODO: what do we do with just masters
                    pass
                elif 'momment' not in p:
                    self.LOGGER.warn(f"Moment not found for {p['image']}")
                    pprint(p, width=256)
                elif 'master' not in p or not p['master']:
                    # self.LOGGER.warn(f"Master not Found {camera}, {p['momment']}, {p['image']}")
                    # pprint(p, width=256)
                    pass
                else:
                    self.LOGGER.warn(f"WHAT A MESS {p['camera']}, {p['momment']}, {p['image']}")
                    # pprint(p, width=256)
                    # exit()
                    # pass
                    
