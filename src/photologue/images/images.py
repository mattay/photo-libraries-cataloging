# from typing import list

from photologue.catalogue.catalogue import Catalogue
from photologue.clean.clean import Clean
from photologue.images.images_utils import file_add_props, group_image_creation  # , process_camera_moments
from photologue.files.files import clean_name, extract_library, is_desired
from photologue.files.files_tag import update_tag
from photologue.momement.moment_martrix import Moment_Matrix

import logging
import re

FilePath = str


class Images:
    def __init__(
        self,
        indexing_cabinate: str,
        raw_extentions: list = [],
        cleanup: dict = {
            'preferred': {},
            'ignore': {},
            'camera_rules': {}
        },
        indexing_cabinate_cleanup=False,
        indexing_cabinate_create=False,
    ):
        self.LOGGER = logging.getLogger('Images')
        self.CATALOGUE = Catalogue(
            indexing_cabinate,
            cleanup=indexing_cabinate_cleanup,
            create=indexing_cabinate_create,
        )
        self.CLEAN = Clean(cleanup['preferred'], cleanup['ignore'], cleanup['camera_rules'])
        self.raw_extentions = raw_extentions
        # self.cleanup = cleanup

    def __list(self) -> list[str]:
        images = self.CATALOGUE.images()
        return images

    # def image_files(self, image: str) -> list[dict]:
    #     return self.CATALOGUE.image_files(image)

    # def list_files(self) -> dict:
    #     return {
    #         i: self.files(i)
    #         for i
    #         in self.__list()
    #     }

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
            'g*******': [],
            'p*******': [],
            '._*': [],
            'other': []
        }

        for image in self.__list():
            number = re.match(r'^\d+$', image)
            dsc = re.match(r'^DSC\d{5}$', image) 		# DSC00857
            _dsc = re.match(r'^_DSC\d{4}', image)		# _DSC1990
            imgp = re.match(r'^IMGP\d{4}$', image)		# IMGP0001
            img_ = re.match(r'^IMG_\d{4}$', image)		# IMG_1890
            gopr = re.match(r'^GOPR\d{4}$', image)		# GOPR0023
            p = re.match(r'^P\d{7}$', image)            # P1000920
            g = re.match(r'^G\d{7}( \d)*$', image)		    # G0093285
            igp = re.match(r'^_IGP\d{4}$', image)       # _IGP0014
            _n = re.match(r'^(\d+_)+n$', image)		    # 162617_10150095509069265_524009264_5821937_4498810_n
            _o = re.match(r'^(\w+_)+o$', image)		    # 243376_10150219436364265_524009264_6908391_1266382_o
            n = re.match(r'^n(\d+_)+\d+', image)        # n737368239_1619563_2369516
            _d = re.match(r'^_[\d_]\d_\d{5}$', image)   # '_10_00030'
            UID = re.match(r'^([A-Z0-9]+-)+([A-Z0-9]+)', image)  # '0BED3F79-451F-4452-83F0-030560A6DAD3',
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
            elif g:
                types['g*******'].append(image)
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
            elif UID:
                types['########-####-####-####-############'].append(image)
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

    def list_cameras(self) -> list[str]:
        return self.CATALOGUE.cameras()

    def list_camera_files(self, camera) -> list:
        return [
            file_add_props(file)
            for file
            in self.CATALOGUE.camera_files(camera)
        ]

    def list_camera_moments(self, camera) -> dict:
        return group_image_creation(self.list_camera_files(camera))

    def add_file(self, image_path: FilePath) -> str | None:
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

        return None

    def add_stats(self, image_path: FilePath, filestats: dict) -> None:
        self.CATALOGUE.add_filestats(image_path, filestats)

    def add_checksum(self, image_path: FilePath, checksum: str) -> None:
        self.CATALOGUE.add_checksum(image_path, checksum)

    def add_exif(self, image_path: FilePath, exif: dict) -> None:
        self.CATALOGUE.add_exif(image_path, exif)

    def check_dup_checksums(self, camera: str, moment: str, matrix: Moment_Matrix) -> None:
        for checksum in matrix.checksums():
            # Remove files already have. Check if there are any left overs
            for f in self.CATALOGUE.checksum_files(camera, checksum):
                if moment != f['date_time_original']:
                    if f['date_time_original']:
                        # There may be an artificial moment generated if there is no 'date_time_original'
                        self.LOGGER.warning("Images [UNEXPECTED] Checksums with different creation date")

                image = f['file_name']
                if image not in matrix.images():
                    self.LOGGER.warning("Images [UNEXPECTED] Image not seen before")
                    break

                found = False
                for matrix_file in matrix.m(image, checksum):
                    if f['file_path'] == matrix_file['file_path']:
                        found = True

                if not found:
                    self.LOGGER.warning("Images [INTERESTING] File not seen before")
                    exit()

    def check_dup_image_names(self, camera: str, moment: str, matrix: Moment_Matrix) -> None:
        for image in matrix.images():
            # Remove files already have. Check if there are any left overs
            for f in self.CATALOGUE.name_files(camera, image):
                if moment != f['date_time_original']:
                    # TODO comparison for images with no creation date!
                    # We know that some cameras have overlaping image names due to rolling over or firmware updates.
                    # Too noisy to log out
                    # self.LOGGER.warning(f"[UNEXPECTED] Image {camera}, {image}, {moment} with different creation date {f['date_time_original']}")
                    continue

                checksum = f['checksum']
                if checksum not in matrix.checksums():
                    self.LOGGER.warning("[UNEXPECTED] Checksum not seen before")
                    break

                found = False
                for matrix_file in matrix.m(image, checksum):
                    if f['file_path'] == matrix_file['file_path']:
                        found = True

                if not found:
                    self.LOGGER.warning("[INTERESTING] File not seen before")
                    exit()

    def process_camera_moment(self, camera: str, moment: str, matrix: Moment_Matrix, tag_state=False) -> dict:

        processed_summary = {
            'masters': 0,
            'copies': 0,
            'ignored': 0,
            'filtered': 0,
            'unresolved': 0
        }

        # Double Checking we have a results for each file to be proccessed.
        # Must be called before processing as file get filtered from the matrix during the process.
        moment_paths = [
            f['file_path']
            for f in matrix.files()
        ]
        # process matrix
        processed = self.CLEAN.proccess_camera_moment_files(camera, moment, matrix)

        master = None

        for p in processed:
            if 'master' in p and p['master']:
                processed_summary['masters'] += 1
                master = p['master']
                moment_paths.remove(master) if master in moment_paths else print("Master not in matrix for", camera, moment, master)

                # self.LOGGER.info("master %s", master)
                self.CATALOGUE.add_relationship(master, 'master')
                if tag_state:
                    update_tag(master, 'master')

                if len(p['copies']) >= 1:
                    processed_summary['copies'] += len(p['copies'])
                    for file_path in p['copies']:
                        moment_paths.remove(file_path) if file_path in moment_paths else print("Copies not in matrix for", camera, moment, file_path)
                        self.CATALOGUE.add_relationship(file_path, 'copy', master)
                        if tag_state:
                            update_tag(file_path, 'copy')

            else:
                if len(p['copies']) >= 1:
                    print("Huh?, only expect to find copies if there is a master")

            if 'ignored' in p:
                processed_summary['ignored'] += len(p['ignored'])
                for file_path in p['ignored']:
                    moment_paths.remove(file_path) if file_path in moment_paths else print("Ignored not in matrix for", camera, moment, file_path)
                    self.CATALOGUE.add_relationship(file_path, 'ignored', master)
                    if tag_state:
                        update_tag(file_path, 'ignored')

            if 'filtered' in p:
                processed_summary['filtered'] += len(p['filtered'])
                for file_path in p['filtered']:
                    moment_paths.remove(file_path) if file_path in moment_paths else print("Filtered not in matrix for", camera, moment, file_path)
                    self.CATALOGUE.add_relationship(file_path, 'filtered', master)
                    if tag_state:
                        update_tag(file_path, 'filtered')

            if 'unresolved' in p:
                processed_summary['unresolved'] += len(p['unresolved'])
                for file_path in p['unresolved']:
                    moment_paths.remove(file_path) if file_path in moment_paths else print("Unresolved not in matrix for", camera, moment, file_path)
                    self.CATALOGUE.add_relationship(file_path, 'unresolved', master)
                    if tag_state:
                        update_tag(file_path, 'unresolved')

            if 'opps' in p:
                print(p['opps'])
                # processed_summary['unresolved'] += len(p['unresolved'])
                # for file_path in p['unresolved']:
                #     self.CATALOGUE.add_relationship(file_path, 'unresolved', master)

        if moment_paths:
            print(camera, moment)
            index = 1
            for mp in moment_paths:
                print(index, mp)
                index += 1

        return processed_summary

    def camera_moment_masters(self, camera: str) -> list:
        return self.CATALOGUE.camera_moment_masters(camera)

    def moment_relationships(self, image_path: FilePath) -> list:
        return self.CATALOGUE.moment_relationships(image_path)

    def add_file_relocation(self, image_path: FilePath, move_to: FilePath) -> None:
        self.CATALOGUE.add_relocation(image_path, move_to)
