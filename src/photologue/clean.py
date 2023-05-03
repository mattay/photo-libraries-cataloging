import logging
from pprint import pprint
from photologue.clean_utils import (
    group_by_checksum,
    group_by_paths,
    list_files,
    matrix_count,
    list_matrix_files,
    group_by_raw_plus_checksums,
    matrix_files,
)


class Clean:
    """For group of images, selected a perfred master"""

    def __init__(self,
                 preferred: dict = {'paths':  [], 'files': []},
                 ignore: dict = {'paths':  [], 'files': []},
                 camera_rules: dict = {},
                 ) -> None:
        self.LOGGER = logging.getLogger('Clean')
        self.camera_rules = camera_rules
        self.preferred = preferred
        self.ignore = ignore

    def cleanup_images(self, files: list) -> None:
        checksums: dict[str, list] = group_by_checksum(files)

        for checksum, files in checksums.items():
            cameras = set()
            images = set()
            for f in files:
                cameras.add(f['camera_model'])
                images.add(f['file_name'])

            if len(cameras) > 1:
                print(f'ERROR - Multiple Cameras for checksum {checksum}')
                break

            camera = next(iter(cameras), None)
            if 'DMC-LX3' in cameras:
                results = self.__filter_camera_files(camera, 'checksum duplicate images', '', files)
                pass
            elif 'PENTAX K10D' in cameras:
                list_files('checksum duplicate images', files)
                pass
            elif 'Canon DIGITAL IXUS 500' in cameras:
                pass
            elif 'iPhone 4S' in cameras:
                pass
            else:
                pprint(files, width=256)
                pass

    def cleanup_matrix(self, matrix: list) -> list:
        cleaned = []
        empty_columns = [True for c in range(len(matrix[0]))]

        for row in range(len(matrix)):
            row_empty = True
            for column in range(len(matrix[row])):
                if len(matrix[row][column]) > 0:
                    # There are files at this vertice
                    row_empty = False
                    empty_columns[column] = False
            if not row_empty:
                cleaned.append(matrix[row])
            # Discard if row is empty

        # Check for empty columns
        for row in cleaned:
            cleaned_columns = []
            for c in range(len(row)):
                column = row.pop(0)
                if empty_columns[c]:
                    # Column needs to be removed
                    break
                cleaned_columns.append(column)
            row = cleaned_columns

        return cleaned

    def proccess_camera_moment_files(self, camera: str, moment: str, matrix: list) -> None:
        results = []
        ignored_files = []
        filtered_matrix = [
            [
                [] for c in range(len(matrix[0]))
            ] for r in range(len(matrix))
        ]
        extentions = set()
        
        # Filter out ignored images
        for row in range(len(matrix)):
            for column in range(len(matrix[row])):
                filtered = []
                for file in matrix[row][column]:
                    if self.__ignore_file(file['file_path']):
                        ignored_files.append(file)
                        continue
                    extentions.add(file['file_extention'])
                    filtered.append(file)
                filtered_matrix[row][column] = filtered

        # Clean up matrix where ignored files leave empty rows or columns
        cleaned_matrix = self.cleanup_matrix(filtered_matrix)        
    
        if not cleaned_matrix:
            self.LOGGER.warn(f'[proccess_camera_moment_files] - Only Ignored Files For -> {camera} -> {moment}')

        elif len(cleaned_matrix) == 1 and len(cleaned_matrix[0]) == 1:
            # Happy Pathcleaned_matrix
            # Nothing tricky to compare yet
            print(f"Moment: {moment}\t Happy Path")
            matrix_count(matrix)
            self.__happy_matrix(moment, cleaned_matrix)
            self.__master_and_copies(
                matrix_files(matrix),
                ignored=ignored_files,
            )
            pass

        elif len(cleaned_matrix) > 1 and len(cleaned_matrix[0]) == 1:
            # single checksum, multiple names, easy
            # - Canon DIGITAL IXUS 500 => 
            # - DMC-LX3 => UID created for photoslibrary files.
            # print(f"Moment: {moment}\tmatrix_size: {matrix_size}")
            print(f"Moment: {moment}\t Multiple Names")
            matrix_count(matrix)
            pass

        elif len(cleaned_matrix) == 1 and len(cleaned_matrix[0]) > 1:
            # One name, Multiple checksums
            # - exports?
            # - Dual Format?
            print(f"Moment: {moment}\t Multiple Checksums")
            print(extentions)
            matrix_count(matrix)
            pass

        else:
            # multiple image names and # One name, Multiple checksums
            # Are they exclusive?
            # print(f"Moment: {moment}")
            print(f"Moment: {moment}\t Multiple Names and Multiple Checksums")
            # matrix_count(matrix)
            pass

        if ignored_files:
            # print(f"Moment: {moment}\t ignored: {len(ignored_files)}")
            list_files(moment, ignored_files)
        #     for f in ignored_files:
        #         print("\t", f['file_name'], f['checksum'], f['file_path'])
        
        return results

    def __happy_matrix(self, moment: str, matrix: list) -> None:
        image_master_file = self.__prefered_master(matrix_files(matrix))
        print(image_master_file)            
        # list_files()
        pass

    def process_camera_image_files(self, camera: str, image: str, files: list[dict]) -> list:
        results = []
        # Get distinct extentions, checksums and
        checksums = set()
        sizes = set()
        extentions = set()
        grouped_checksum: dict[str, list] = {}
        ignored = []
        filtered = []

        for f in files:
            # Check if file should be ignored
            # FIXME: do this
            if self.__ignore_file(f['file_path']):
                ignored.append(f)
                continue

            filtered.append(f)
            checksums.add(f.get('checksum'))
            sizes.add(f.get('size'))
            extentions.add(f.get('file_extention'))
            # Group by checksums
            c = str(f.get('checksum', 0))
            g = grouped_checksum.get(c, [])
            g.append(f)
            grouped_checksum[c] = g

        # Multiple Extentions -> Exports or RAW+
        if len(extentions) > 1:
            mutiple_extentions = self.__mutiple_extentions(camera, image, extentions, filtered)

            if len(mutiple_extentions) == 1:
                r = mutiple_extentions[0]
                r['ignored'] = ignored
                results.append(r)

            else:
                if ignored:
                    self.LOGGER.warn(f'[process_camera_images] - {camera} - Ignored files - mutiple_extentions {len(mutiple_extentions)}')
                    list_files('ignored', ignored)
                    # list_files('filtered', filtered)
                for m in mutiple_extentions:
                    results.append(m)

        # Multiple checksums
        elif len(checksums) > 1 or len(sizes) > 1:
            multiple_checksums = self.__multiple_checksums(camera, image, filtered)

            if len(multiple_checksums) == 1:
                r = multiple_checksums[0]
                r['ignored'] = ignored
                results.append(r)

            else:
                if ignored:
                    self.LOGGER.warn(f'[process_camera_images] - {camera} - Ignored files - multiple_checksums {len(multiple_checksums)}')
                    list_files('ignored', ignored)
                    # list_files('filtered', filtered)
                for m in multiple_checksums:
                    results.append(m)

        # Duplicates
        elif filtered:
            r = self.__clean_images(filtered, ignored)
            results.append(r)

        else:
            self.LOGGER.warn(f'[process_camera_images] - Only Ignored Files For -> {camera} -> {image}')
            r = {
                'master': [],
                'copies': [],
                'ignored': ignored,
                'filtered': [],
                'unresolved': [],
            }
            results.append(r)

        return results

    def __mutiple_extentions(self, camera: str, image: str, extentions: set, files: list) -> list[dict]:

        results = []
        # RAW+
        if extentions in [{'.RW2', '.JPG'}, {'.PEF', '.JPG'}, {'.DNG', '.JPG'}, {'.jpg', '.RW2', '.JPG'}]:
            results.extend(self.__dirty_RAW_plus(image, files))  # FIXME: Return Value

        else:
            filtered_files = self.__filter_camera_files(camera, 'extentions', extentions, files)
            keep = filtered_files['keep']
            filtered = filtered_files['ignore']
            checksums = {
                f.get('checksum')
                for f in keep
            }

            if not keep:
                self.LOGGER.error('[Mutiple Extentions] - Unexpected State - filter_camera_file returned no files')
                exit()

            elif len(checksums) == 1:
                r = self.__master_and_copies(keep, filtered=filtered)
                results.append(r)

            else:
                self.LOGGER.error(f'[Mutiple Extentions] -> Multiple Checksums {list(extentions)}')

                multiple_checksums = self.__multiple_checksums(camera, image, files)  # __multiple_checksums filters files too.

                if len(multiple_checksums) == 1:
                    r = multiple_checksums[0]
                    results.append(r)

                else:
                    self.LOGGER.warn('[Mutiple Extentions] - multiple_checksums - multiple results')
                    list_files(image, keep)
                    r = {
                        'master': '',
                        'copies': [],
                        'ignored': [],
                        'filtered': filtered,
                        'unresolved': keep,
                    }
                    results.append(r)

        return results

    def __multiple_checksums(self, camera: str, image: str, files: list) -> list[dict]:
        results = []

        filtered_files = self.__filter_camera_files(camera, 'checksums', None, files)
        keep = filtered_files['keep']
        filtered = filtered_files['ignore']
        checksums = {
            f.get('checksum')
            for f in keep
        }

        if not keep:
            self.LOGGER.error('[Mutiple Checksums] - Unexpected State - filter_camera_file returned no files')

        elif len(checksums) == 1:
            r = self.__master_and_copies(keep, filtered=filtered)  # FIXME: Return Value
            results.append(r)

        else:
            copies = self.__tagged_copies(image, keep, filtered)
            if len(copies) == 1:
                results.append(copies[0])
            else:
                self.LOGGER.error('[Mutiple Checksums] - Mutiple Tagged Copies')
            # results.append(self.__tagged_copies(image, keep))  # FIXME: Return Value

        return results

    def __clean_images(self, files: list, ignored: list = [], filtered: list = []) -> dict[str, str | list]:
        return self.__master_and_copies(files, ignored=ignored, filtered=filtered)

    def __dirty_RAW_plus(self, image: str, files: list) -> list:
        results: list[dict] = []
        paths: dict[str, dict] = group_by_paths(files)
        paired = {}
        singles = {}

        # Seperate paired and single
        for path, ext in paths.items():
            if len(ext.keys()) == 2:
                paired[path] = ext
            else:
                singles[path] = ext

        if paired:
            checksums = group_by_raw_plus_checksums(paired)
            raw = checksums['raw']
            jpg = checksums['jpg']

            if len(raw) == 1 and len(jpg) == 1:
                results.append(self.__clean_images(list(raw.values())[0]))
                results.append(self.__clean_images(list(jpg.values())[0]))

            else:
                self.LOGGER.error(f'[RAW+] -> Paired have multiple checksums for {image}')
                list_files(image, files)

        # Called after Paired to be able to match to paired
        if singles:
            # Index checksums to copies
            paired_checksums: dict = {}
            for r in results:
                for f in files:
                    if f['file_path'] == r['master']:
                        paired_checksums[f['checksum']] = r['copies']

            extentision: dict = {}
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
                        e = extentision.get(ext, {})
                        c = e.get(checksum, [])
                        e[checksum] = c
                        extentision[ext] = e
                        extentision[ext][checksum].append(file)

            # NO - Checksum matched a paired
            if extentision:
                # Keeping Both
                for ext, checksums in extentision.items():
                    if len(checksums.keys()) == 1:
                        for checksum, file_list in checksums.items():
                            results.append(self.__clean_images(file_list))
                    else:
                        self.LOGGER.error(f'[RAW+] -> Expected only a single checksums for extention {ext} of {list(extentision.keys())}  for {image}')
                        list_files(image, files)

        if not singles and not paired:
            self.LOGGER.error('[RAW+] -> Expeced Singels or Paired, Neither found for {image}')
            list_files(image, files)

        return results

    def __tagged_copies(self, image: str, files: list, filtered: list) -> list[dict]:
        results = []
        # tagged_copies = [] # FIXME:
        by_checksums = group_by_checksum(files)

        if not by_checksums:
            self.LOGGER.warn(f'[Tagged Copies] - including "copy" for {image}')

        if len(by_checksums.keys()) == 1:
            only_checksum = list(by_checksums.keys())[0]
            r = self.__clean_images(by_checksums[only_checksum], filtered=filtered)
            results.append(r)

        elif len(by_checksums.keys()) > 1:
            self.LOGGER.warn(f'[Tagged Copies] - Multiple Checksums for {image} = {list(by_checksums.keys())}')
            list_files(f'[Tagged Copies] -- {list(by_checksums.keys())}', files)
            r = {
                'master': '',
                'copies': [],
                'ignored': [],
                'filtered': filtered,
                'unresolved': files,
            }
            results.append(r)

        else:
            self.LOGGER.error(f'[Tagged Copies] - No checksums for {image}')
            # list_files('Tagged Copies', tagged_copies)
            r = {
                'master': '',
                'copies': [],
                'ignored': [],
                'filtered': filtered,
                'unresolved': files,
            }
            results.append(r)
            # TODO:

        return results

    def __master_and_copies(self,
                            files: list,
                            copies: list = [],
                            ignored: list = [],
                            filtered: list = []) -> dict[str, str | list]:
        image_master_file: str = ''
        image_copies: list[str] = copies
        image_ignored: list[str] = ignored
        image_filtered: list[str] = filtered

        if len(files) == 1:
            f = files[0]
            image_master_file = f['file_path']

        else:
            image_master_file = self.__prefered_master(files)

            #  Exclude Master
            image_copies = [
                f['file_path']
                for f
                in files
                if f['file_path'] != image_master_file
            ]

        return {
            'master': image_master_file,
            'copies': image_copies,
            'ignored': image_ignored,
            'filtered': image_filtered
        }

    def __prefered_master(self, files: list) -> str:
        """Identify a master image file"""
        image_master_file = ''

        for preferred in self.preferred['paths']:
            if image_master_file:
                break

            for f in files:
                path = f['file_path']
                if f['copy']:
                    continue  # Ignore copies

                if preferred in path:
                    image_master_file = path
                    break

        if not image_master_file:
            self.LOGGER.error('[Prefered Master] - No master file identified')
            list_files('Prefered Master', files)
            pass

        return image_master_file

    def __filter_camera_files(self, camera, condition, matches, files) -> dict:
        rules = []
        results = {
            'keep': [],
            'ignore': []
        }

        if camera not in self.camera_rules:
            self.LOGGER.error('[Configuration] - Camera not found in "cleanup.camera_rules"')
        else:
            # collect Rules
            for filter in self.camera_rules[camera].get('filters', []):
                if filter['condition'] == condition and filter['matches'] == matches:
                    rules.append(filter)

        if not rules:
            results['keep'] = files
            return results

        files_keep = []
        files_ignore = []
        for rule in rules:
            if rule['action'] == 'keep':
                for f in files:
                    rule_holds = True
                    for key, value in rule['file_props'].items():
                        if f[key] != value:
                            rule_holds = False
                            break
                    if rule_holds:
                        files_keep.append(f)

            #  Only keep the from the first rule thats true
            if files_keep:
                break

        if not files_keep:
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
                            files_ignore.append(f)

        if not files_keep and not files_ignore:
            # Nothing filtered -> Everything kept
            files_keep = files

        elif files_keep:
            # We know what to keep, what is left we'll ignore
            for f in files:
                if f not in files_keep:
                    files_ignore.append(f)

        elif files_ignore:
            # We know what to ignore, what is left we'll keep
            for f in files:
                if f not in files_ignore:
                    files_keep.append(f)

        results['keep'] = files_keep
        results['ignore'] = files_ignore

        return results

    def __ignore_file(self, file_path: dict) -> bool:
        ignore = False
        if file_path in self.ignore['files']:
            # self.LOGGER.info(f'Ignored file >> {file_path}')
            ignore = True
        elif self.ignore['paths']:
            for path in self.ignore['paths']:
                if path in file_path:
                    # self.LOGGER.info(f'Ignored file in path >> {file_path}')
                    ignore = True

        return ignore
