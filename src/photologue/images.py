# from typing import list

from photologue.catalogue import Catalogue
from photologue.clean import Clean
from photologue.images_utils import group_files_by_image_date
from photologue.files import clean_name, extract_library, is_desired

import logging
import re
# from pprint import pprint


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
        self.cleanup = cleanup

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
        library = extract_library(image_path)
        file = clean_name(image_path)

        if is_desired(file, library):
            file['raw_image'] = True if file['extention'] in self.raw_extentions else False
            self.CATALOGUE.add_file(file)
            self.CATALOGUE.add_library(image_path, library)
            return image_path

    def add_stats(self, image_path: str, filestats: dict) -> None:
        self.CATALOGUE.add_filestats(image_path, filestats)

    def add_checksum(self, image_path: str, checksum: str) -> None:
        self.CATALOGUE.add_checksum(image_path, checksum)

    def add_exif(self, image_path: str, exif: dict) -> None:
        self.CATALOGUE.add_exif(image_path, exif)

    def process_images(self) -> None:
        summary = []
        self.CATALOGUE.clear_relationship()
        for camera in self.CATALOGUE.cameras():
            camera_files = self.CATALOGUE.camera_files(camera)
            collected = group_files_by_image_date(camera_files)
            s = {
                'camera': camera,
                'countof': {
                    'files': len(camera_files),
                    'images': len(collected.keys()),
                    'momments': 0,
                    'masters': 0,
                    'copies': 0,
                    'filtered': 0,
                    'ignored': 0,
                    'unresolved': 0
                }
            }

            for image, datetimes in collected.items():
                for momment, files in datetimes.items():
                    s['countof']['momments'] += 1
                    processed_counts = self.process_camera_image(camera, image, files)
                    for processed, count in processed_counts.items():
                        s['countof'][processed] += count
                    # pass

            summary.append(s)
        self.log_process_summary(summary)

    def process_camera_image(self, camera: str, image: str, files: list[dict]) -> dict:
        processed = self.CLEAN.process_camera_image_files(camera, image, files)
        processed_counts = {
            'masters': 0,
            'copies': 0,
            'ignored': 0,
            'filtered': 0,
            'unresolved': 0
        }

        master = None
        for p in processed:

            if 'master' in p and p['master']:
                processed_counts['masters'] += 1
                master = p['master']
                self.CATALOGUE.add_relationship(master, 'master')

                if len(p['copies']) >= 1:
                    processed_counts['copies'] += len(p['copies'])
                    for file_path in p['copies']:
                        self.CATALOGUE.add_relationship(file_path, 'copy', master)

            if 'ignored' in p:
                processed_counts['ignored'] += len(p['ignored'])
                for file in p['ignored']:
                    self.CATALOGUE.add_relationship(file['file_path'], 'ignored', master)

            if 'filtered' in p:
                processed_counts['filtered'] += len(p['filtered'])
                for file in p['filtered']:
                    self.CATALOGUE.add_relationship(file['file_path'], 'filtered', master)

            if 'unresolved' in p:
                processed_counts['unresolved'] += len(p['unresolved'])
                for file in p['unresolved']:
                    self.CATALOGUE.add_relationship(file['file_path'], 'unresolved', master)

        return processed_counts

    def log_process_summary(self, summary: list) -> None:
        # Summary
        totals = {
            'cameras': 0,
            'files': 0,
            'images': 0,
            'momments': 0,
            'masters': 0,
            'copies': 0,
            'filtered': 0,
            'ignored': 0,
            'unresolved': 0,
            'opps': 0
        }
        
        self.LOGGER.info("Process Summary")
        for s in summary:
            oops = s['countof']['files']
            oops -= s['countof']['masters']
            oops -= s['countof']['copies']
            oops -= s['countof']['filtered']
            oops -= s['countof']['ignored']
            oops -= s['countof']['unresolved']

            for of, count in s['countof'].items():
                totals[of] = totals[of] + count | count
            totals['cameras'] += 1
            totals['opps'] += oops

            self.LOGGER.info(" | ".join([
                f"{s['camera']:<28}",
                f"Images {s['countof']['images']:>6,}",
                f"Momments {s['countof']['momments']:>6,}",
                f"Files {s['countof']['files']:>7,}",
                f"Masters {s['countof']['masters']:>6,}",
                f"Copies {s['countof']['copies']:>7,}",
                f"Filtered {s['countof']['filtered']:>6,}",
                f"Ignored {s['countof']['ignored']:>6,}",
                f"Unresolved {s['countof']['unresolved']:>4,}",
                f"Oops {oops:>7,}"
            ]))

        self.LOGGER.info(" | ".join([
            f"TOTALS{totals['cameras']:>22}",
            f"TOTAL  {totals['images']:>6,}",
            f"TOTAL    {totals['momments']:>6,}",
            f"TOTAL {totals['files']:>7,}",
            f"TOTAL   {totals['masters']:>6,}",
            f"TOTAL  {totals['copies']:>7,}",
            f"TOTAL    {totals['filtered']:>6,}",
            f"TOTAL   {totals['ignored']:>6,}",
            f"TOTAL      {totals['unresolved']:>4,}",
            f"TOTAL{totals['opps']:>7,}"
        ]))
