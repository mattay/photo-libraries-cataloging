import logging
# from pprint import pprint
# from datetime import datetime
import os


class Clean:
    """For group of images, selected a perfred master"""

    def __init__(self,
                 preferred: dict = {'paths':  [], 'files': []},
                 ignore: dict = {'paths':  [], 'files': []},
                 camera_rules: dict = {},
                 ) -> None:
        self.LOGGER = logging.getLogger('Clean')
        self.camera_models: dict[str, dict] = {}
        self.camera_rules = camera_rules
        self.preferred = preferred
        self.ignore = ignore

    def add_camera_models(self, models: list):
        self.camera_models = {
            camera: {}
            for camera
            in models
        }

    def rules(self) -> dict:
        for camera in self.camera_models:
            if camera not in self.camera_rules:
                self.LOGGER.warn(f'No rules defined yet for camera "{camera}"')

        return self.camera_models

    def collect_image_date_files(self, images: list[dict]) -> dict:
        """Organises files into a heiarchy of Images then date/time and files

            Parameters
            ----------
            images : list[dict]
                list of files

            Returns
            -------
            dict
                heireacy {image: {moment: [files]}}
            """
        collected: dict[str, dict] = {}

        for file in images:
            # Check if file shoule be ignored
            if self.ignore_file(file['file_path']):
                break

            # clean up dates
            file['image_date'] = self.original_date(file['date_time_original'])
            file['mod_date'] = self.original_date(file['date_time_modifed'])
            # Calculate if file has been modified
            file['modified'] = 1 if file['image_date'] != file['mod_date'] else 0

            # Add to Hhiarchy
            i = collected.get(file['file_name'], {})
            t = i.get(file['date_time_original'], [])
            t.append(file)

            i[file['date_time_original']] = t
            collected[file['file_name']] = i

        return collected

    def process_camera_images(self, camera: str, images: list[dict]) -> None:
        collected = self.collect_image_date_files(images)
        results = []
        if collected:
            clean_copies = 0
            dirty_copies = 0
            ignored_copies = 0

            for image, datetimes in collected.items():
                for momment, files in datetimes.items():
                    # files = self.__pre_process(moment_files)

                    # Get distinct extentions, checksums and
                    checksums = set()
                    sizes = set()
                    extentions = set()
                    grouped_checksum: dict[str, list] = {}

                    for f in files:
                        checksums.add(f.get('checksum'))
                        sizes.add(f.get('size'))
                        extentions.add(f.get('file_extention'))
                        # Group by checksums
                        c = f.get('checksum')
                        g = grouped_checksum.get(c, [])
                        g.append(f)
                        grouped_checksum[c] = g

                    # Multiple Extentions -> Exports or RAW+
                    if len(extentions) > 1:
                        dirty_copies += 1
                        results.extend(self.__mutiple_extentions(camera, image, extentions, files))

                    # Multiple checksums
                    elif len(checksums) > 1 or len(sizes) > 1:
                        dirty_copies += 1
                        results.extend(self.__multiple_checksums(camera, image, files))

                    # Duplicates
                    elif files:
                        clean_copies += 1
                        results.append(self.__clean_images(files))

                    else:
                        ignored_copies += 1
                        # FIXME:
                        self.LOGGER.warn(f'[process_camera_images] - Only Ignored Files For -> {camera} -> {image}')

            # Summary
            self.LOGGER.info("    ".join([
                f'{camera:<26}',
                f'collected {len(collected):>5}',
                f'clean {clean_copies:>5}',
                f'dirty {dirty_copies:>5}',
                f'ignored {ignored_copies:>5}'
            ]))

    def __mutiple_extentions(self, camera: str, image: str, extentions: set, files: list) -> list[dict]:

        results = []
        # RAW+
        if extentions in [{'.RW2', '.JPG'}, {'.PEF', '.JPG'}, {'.DNG', '.JPG'}, {'.jpg', '.RW2', '.JPG'}]:
            results.extend(self.__dirty_RAW_plus(image, files))  # FIXME: Return Value

        else:
            filtered_files = self.__filter_camera_files(camera, 'extentions', extentions, files)

            if extentions in [{'.jpg', '.RW2', '.JPG'}]:
                results.extend(self.__dirty_RAW_plus(image, filtered_files))  # FIXME: Return Value
            else:
                if camera == 'DMC-LX3':
                    results.append(self.__tagged_copies(image, filtered_files))  # FIXME: Return Value

        return results

    def __multiple_checksums(self, camera: str, image: str, files: list) -> list[dict]:
        results = []
        filtered_files = self.__filter_camera_files(camera, 'checksums', None, files)
        results.append(self.__tagged_copies(image, filtered_files))  # FIXME: Return Value

        return results

    def __clean_images(self, files: list) -> dict[str, str | list]:
        return self.__master_and_copies(files)

    def __dirty_RAW_plus(self, image: str, files: list) -> list:
        results: list[dict] = []
        paths: dict[str, dict] = {}
        paired = {}
        singles = {}

        # Looking for raw files with matching jpeg file in same directory
        for f in files:
            dir = os.path.dirname(f['file_path'])
            d = paths.get(dir, {})
            d[f.get('file_extention')] = f
            paths[dir] = d

        # Seperate paired and single
        for path, ext in paths.items():
            if len(ext.keys()) == 2:
                paired[path] = ext
            else:
                singles[path] = ext

        if paired:
            checksums = self.__raw_plus_checksums(paired)
            raw = checksums['raw']
            jpg = checksums['jpg']

            if len(raw) == 1 and len(jpg) == 1:
                results.append(self.__clean_images(list(raw.values())[0]))
                results.append(self.__clean_images(list(jpg.values())[0]))

            else:
                self.LOGGER.error('[RAW+] -> Paired have multiple checksums for {image}')
                # print("\t RAW")
                # pprint(raw)
                # print("\t JPG")
                # pprint(jpg)

        # Called after Paired to be able to match to paired
        if singles:
            # Index checksums to copies
            paired_checksums: dict = {}
            for r in results:
                for f in files:
                    if f['file_path'] == r['master']:
                        paired_checksums[f['checksum']] = r['copies']

            extentision: dict[str, dict] = {}
            # YES - Checksum matched a paired
            for single in singles.values():
                for file in single.values():
                    checksum = file['checksum']
                    ext = file['file_extention']
                    path = file['file_path']

                    if checksum in paired_checksums.keys():
                        paired_checksums[checksum].append(path)
                    else:
                        #  Solve by extentions -> checksums?
                        # if ext in extentision:
                        # e = extentision[ext] or {}
                        # c = e[checksum] or []
                        # c
                        # e
                        extentision[ext][checksum].append(file)

            # NO - Checksum matched a paired
            if extentision:
                # Keeping Both
                for ext, checksums in extentision.items():
                    if len(checksums.keys()) == 1:
                        for checksum, file_list in checksums.items():
                            # print(type(file_list))
                            # pprint(file_list)
                            results.append(self.__master_and_copies(file_list))
                    else:
                        self.LOGGER.error(f'[RAW+] -> Expected only a single checksums for extention {ext} of {list(extentision.keys())}  for {image}')
                        # for checksum, file_list in checksums.items():
                        #     self.__list_files(checksum, file_list)

        if not singles and not paired:
            self.LOGGER.error('[RAW+] -> Expeced Singels or Paired, Neither found for {image}')

        return results

    def __tagged_copies(self, image, files: list,) -> dict[str, str | list]:
        results = {}
        # tagged_copies = [] # FIXME:
        by_checksums = self.__group_by_checksum(files)

        if not by_checksums:
            self.LOGGER.warn(f'[Tagged Copies] - including "has_copy_in_subfix" for {image}')
            by_checksums = self.__group_by_checksum(files)

        if len(by_checksums.keys()) == 1:
            only_checksum = list(by_checksums.keys())[0]
            results = self.__clean_images(by_checksums[only_checksum])
            # Add tagged_copies to copies
            # results['copies'] = results['copies'] + [file['file_path'] for file in tagged_copies]

        elif len(by_checksums.keys()) > 1:
            self.LOGGER.error(f'[Tagged Copies] - Multiple Checksums for {image}')
            self.__list_files(f'[Tagged Copies] -- {list(by_checksums.keys())}', files)

        else:
            self.LOGGER.error(f'[Tagged Copies] - No checksums for {image}')
            # self.__list_files('Tagged Copies', tagged_copies)

            # TODO:

        return results

    # def __filter_out_tag(self, files: list, filter_out_tag: str='') -> dict())

    def __group_by_checksum(self, files: list, filter_out_tag: str = '') -> dict[str, list]:
        results: dict[str, list] = {}
        for file in files:
            if filter_out_tag and file[filter_out_tag]:
                # Will add to copies if only a single checksum exists
                break
            else:
                checksum = file['checksum']
                checksum_files = results.get(checksum, [])
                checksum_files.append(file)
                results[checksum] = checksum_files

        return results

    def __master_and_copies(self, files: list) -> dict[str, str | list]:
        image_master_file: str = ''
        image_copies: list[str] = []

        if len(files) == 1:
            f = files[0]
            image_master_file = f['file_path']

        else:
            image_master_file = self.__prefered_master(files)

            #  Exclude Master
            image_copies = [f['file_path']
                            for f
                            in files
                            if f['file_path'] != image_master_file
                            ]

        return {
            'master': image_master_file,
            'copies': image_copies
        }

    def __prefered_master(self, files: list) -> str:
        """Identify a master image file"""
        image_master_file = ''

        for preferred in self.preferred['paths']:
            if image_master_file:
                break

            for f in files:
                # preferred_rules = {}
                path = f['file_path']

                if preferred in path:
                    image_master_file = path
                    # if 'path'in preferred_rules:
                    #     preferred_rules['path'].append(path)
                    # else:
                    #     preferred_rules['path'] = [path]
                    break

                # f['preferred_rules'] = preferred_rules

        if not image_master_file:
            # self.LOGGER.error(f'[Prefered Master] - No master file identified')
            pass
            # self.__list_files('Prefered Master', files)
            # exit()

        return image_master_file

    def __raw_plus_checksums(self, paired: dict) -> dict[str, dict]:
        r_checksums: dict[str, list] = {}
        j_checksums: dict[str, list] = {}

        # Pair RAW+ files
        for p, e in paired.items():
            exts = list(e.keys())
            j = None
            r = None
            if exts[0] == '.JPG':
                r = exts[1]
                j = exts[0]
            else:
                r = exts[0]
                j = exts[1]

            rf = paired[p][r]
            jf = paired[p][j]
            rc = r_checksums.get(rf['checksum'], [])
            jc = j_checksums.get(jf['checksum'], [])
            rc.append(rf)
            jc.append(jf)
            r_checksums[rf['checksum']] = rc
            j_checksums[jf['checksum']] = jc

        return {
            'raw': r_checksums,
            'jpg': j_checksums
        }

    def __filter_camera_files(self, camera, condition, matches, files) -> list:
        rules = []
        results = []

        if camera not in self.camera_rules:
            self.LOGGER.error('[Configuration] - Camera not found in "cleanup.camera_rules"')
        else:
            # collect Rules
            for filter in self.camera_rules[camera].get('filters', []):
                if filter['condition'] == condition and filter['matches'] == matches:
                    rules.append(filter)

        if not rules:
            return files

        files_kept = []
        for rule in rules:
            if rule['action'] == 'keep':
                # if camera == 'QSS':
                #     print('QSS')
                for f in files:
                    rule_holds = True
                    for key, value in rule['file_props'].items():
                        if f[key] != value:
                            rule_holds = False
                            break
                    if rule_holds:
                        files_kept.append(f)

            #  Only keep the from the first rule thats true
            if files_kept:
                break

        if not files_kept:
            files_ignored = []
            # Remove any ignore rules instead
            for rule in rules:
                if rule['action'] == 'ignore':
                    for f in files:
                        rule_holds = True
                        for key, value in rule['file_props'].items():
                            if f[key] != value:
                                rule_holds = False
                                break
                        if rule_holds:
                            files_ignored.append(f)
            for f in files:
                if f not in files_ignored:
                    results.append(f)
        else:
            results = files_kept

        if not results:
            self.LOGGER.error('[Filter Camera File] - No Results')
            # pprint(rules)
            # self.__list_files('[filter_camera_file]', files)
            # exit()
            # else:
            #     self.LOGGER.info(f"Ignored {f['file_path']}")

        # if camera == 'QSS':
        #     pprint(rules)
        #     # pprint(results)
        #     exit()

        return results

    def original_date(self, date_time_original: str) -> object:
        date = '    :  :  '
        if date_time_original == '-':
            pass
        elif date_time_original == '    :  :     :  :':
            pass
        elif date_time_original:
            date = date_time_original[:10]
        return date

    def ignore_file(self, file_path: dict) -> bool:
        ignore = False
        if file_path in self.ignore['files']:
            self.LOGGER.info(f'Ignored file >> {file_path}')
            ignore = True
        elif self.ignore['paths']:
            for path in self.ignore['paths']:
                if path in file_path:
                    self.LOGGER.info(f'Ignored file >> {file_path}')
                    ignore = True

        return ignore

    def __list_files(self, group: str, files: list):
        print(group)
        print("  DATE       MOD DATE   M CHECKSUM     C SOFTWARE         QUALITY  COLOURSPACE  FILE PATH")
        print("  ---------- ---------- - ------------ - ---------------- -------- ------------ ------------------------------------------------")
        [print(f"  {file['image_date']} {file['mod_date']} {file['modified']} {file['checksum']:>12} {file['has_copy_in_subfix']}" +
               f" {str(file['software']):<16} {str(file['quality']):<8} {str(file['color_space']):<12} {file['file_path']}")
            for file
            in sorted(files, key=lambda d: d['checksum'])
         ]


# {'-': {},
#  '<VLUU L830  / Samsung L830>': {},
#  'CYBERSHOT': {},
#  'Canon DIGITAL IXUS 500': {},
#  'Canon DIGITAL IXUS 55': {},
#  'Canon DIGITAL IXUS 80 IS': {},
#  'Canon EOS 60D': {},
#  'Canon PowerShot A720 IS': {},
#  'Canon PowerShot G9': {},
#  'DCR-TRV340E': {},
#  'DMC-FX12': {},
#  'DMC-LX3': {},
#  'DMC-TZ15': {},
#  'DMC-TZ2': {},
#  'DMC-ZS7': {},
#  'DiMAGE X': {},
#  'FinePix S5600': {},
#  'HERO4 Silver': {},
#  'IWS': {},
#  'PENTAX K-5': {},
#  'PENTAX K10D': {},
#  'PENTAX K200D': {},
#  'QSS': {},
#  'iPhone': {},
#  'iPhone 3G': {},
#  'iPhone 4S': {},
#  'iPhone 5s': {},
#  'iPhone 6': {},
#  'iPhone 6s': {},
#  'u770SW,S770SW': {}}
