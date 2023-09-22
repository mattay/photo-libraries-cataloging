# from typing import Set, Tuple
import logging
from photologue.clean.clean_utils import (
    list_files,
    are_files_incrementing
)
from photologue.clean.clean_group import (
    group_by_paths,
    group_by_raw_plus_checksums,
)
from photologue.clean.clean_filtering import ignore_file, filter_out, filter_camera_files
from photologue.momement.moment_martrix import Moment_Matrix
from pprint import pprint


class Clean:
    """For group of images, selected a perfred master"""
    LOGGER = logging.getLogger('Clean')

    def __init__(self,
                 preferred: dict = {'paths':  [], 'files': []},
                 ignore: dict = {'paths':  [], 'files': []},
                 camera_rules: dict = {},
                 ) -> None:
        self.camera_rules = camera_rules
        self.preferred = preferred
        self.ignore_rules = {
            'paths': ignore['paths'] if ignore['paths'] else [],
            'files': ignore['files'] if ignore['files'] else []
        }

    def rules(self, camera, condition, matches) -> list:
        rules = []
        if camera in self.camera_rules.keys():
            for filter in self.camera_rules[camera].get('filters', []):
                if filter['condition'] == condition and filter['matches'] == matches:
                    rules.append(filter)
        # else:
        #     self.LOGGER.info(f'No rules set for Camera "{camera}"')
        return rules

    def proccess_camera_moment_files(self, camera: str, moment: str, matrix: Moment_Matrix) -> list:
        # Returning results
        results: list = []

        # Remove specific file paths from the matrix that we want to ignore.
        ignored_files = matrix.ignore(ignore_file, self.ignore_rules)
        filtered_files = []

        #
        #  IMPORTANT !
        #
        # matrix.filter() that takes __filter_for() removes indivdual files that match the rules.
        # __filter_camera_files filters a list of files that must match the first rule that is satisfied.
        filtered_files += matrix.filter(filter_out, (self.rules(camera, 'copies', None)))
        filtered_files += matrix.filter(filter_out, (self.rules(camera, 'names', None)))

        moment_files = matrix.files()
        checksum_count = len(matrix.checksums())

        if checksum_count > 1:
            # Pre-filter now that we won't be using the matrix again.
            # Filter images with camera filter rule sets defined in config.xml
            filtering = filter_camera_files(self.camera_rules.get(camera, {}), 'software', None, moment_files)
            moment_files = filtering['keep']
            filtered_files += filtering['ignore']

            filtering = filter_camera_files(self.camera_rules.get(camera, {}), 'checksums', None, moment_files)
            moment_files = filtering['keep']
            filtered_files += filtering['ignore']

        # Split moments on sequnce and recall function again for each sequence.
        if are_files_incrementing(moment_files):
            # Some GoPro sequences share the same moments
            # Some PENTAX K*D sequences share the same moments
            # QSS images that don't have moments become sequences based on image names
            results = results + self.__sequence(camera, moment, moment_files, ignored_files, filtered_files)

        else:
            results = results + self.process_moment(camera, moment, moment_files, ignored_files, filtered_files)

        if ignored_files and not results:
            list_files(f"[{camera}]\tMoment: {moment}\t Ignored and No Results", moment_files, ignored_files + filtered_files)
            # TODO:
            # pass

        return results

    def process_moment(self, camera, moment, moment_files, ignored_files, filtered_files) -> list:
        results = []

        # recalculate counts
        moment_images: dict = {}
        moment_checksums: dict = {}
        moment_extentions: dict = {}

        for file in moment_files:
            moment_images[file['file_name']] = moment_images.get(file['file_name'], []) + [file]
            moment_checksums[file['checksum']] = moment_images.get(file['checksum'], []) + [file]
            moment_extentions[file['file_extention']] = moment_images.get(file['file_extention'], []) + [file]

        image_count = len(moment_images)
        checksum_count = len(moment_checksums)
        extentions_count = len(moment_extentions)

        r = {
            'master': [],
            'copies': [],
            'ignored': [f['file_path'] for f in ignored_files],
            'filtered': [f['file_path'] for f in filtered_files],
            'unresolved': []
        }

        if not moment_files:
            list_files(f"[{camera}]\tMoment: {moment}\t Only Ignored Files", moment_files, ignored_files + filtered_files)
            results.append(r)

        elif moment == '    :  :     :  :':
            # self.LOGGER.warn(f'[proccess_camera_moment_files] - Moment undefined -> {camera} -> {moment} - {len(moment_files)} ')
            if checksum_count == 1:
                r = self.__master_and_copies(moment_files, ignored=ignored_files, filtered=filtered_files)
                if not r['master']:
                    list_files(f"[{camera}]\tMoment: {moment}\t No Master Picked!", moment_files)
            else:
                list_files(f"[{camera}]\tMoment: {moment}\t - Moment undefined ", moment_files, ignored_files + filtered_files)
                r['unresolved'] = [f['file_path'] for f in moment_files]

            results.append(r)

        # Everything should be a copy of each other.
        elif checksum_count == 1:
            r = self.__master_and_copies(moment_files, ignored=ignored_files, filtered=filtered_files)
            if not r['master']:
                list_files(f"[{camera}]\tMoment: {moment}\t No Master Picked!", moment_files)
            results.append(r)

        #  Expect to be RAW+
        elif extentions_count > 1:
            # Check for paired extention in config
            if moment_extentions.keys() in self.__camera_extention(camera):
                # __RAW_plus will return a list, one for RAW and one for the mactching JPG
                for r in self.__RAW_plus(moment, moment_files, ignored_files, filtered_files):
                    if not r['master']:
                        list_files(f"[{camera}]\tMoment: {moment}\t No Master Picked!", moment_files, ignored_files + filtered_files)
                    results.append(r)  # = results + self.__RAW_plus(moment, moment_files, ignored_files, filtered_files)
            else:
                list_files(f"[{camera}]\tMoment: {moment}\t [Extentions] {list(moment_extentions.keys())}", moment_files, ignored_files + filtered_files)

        # One name, Multiple checksums
        elif image_count == 1 and checksum_count > 1:
            # TODO: What to do with multiple checksums
            # print(f"[{camera}]\tMoment: {moment}\t 1 Image, Many Checksums!")
            list_files(f"[{camera}]\tMoment: {moment}\t 1 Image, Many Checksums!", moment_files, ignored_files+filtered_files)
            # r['unresolved'] = [f['file_path'] for f in moment_files]
            pass

        elif image_count == checksum_count:
            for image in moment_images:
                r = self.__master_and_copies(moment_images[image], ignored=ignored_files, filtered=filtered_files)
                if not r['master']:
                    list_files(f"[{camera}]\tMoment: {moment}\t No Master Picked!", moment_files)
                results.append(r)

        # multiple image names and # One name, Multiple checksums
        else:
            print("Oh no :(")
            list_files(f"[{camera}]\tMoment: {moment}\t ???", moment_files, ignored_files + filtered_files)

        return results

    def __RAW_plus(self, moment, files: list, ignored: list = [], filtered: list = []) -> list:
        files_paths = group_by_paths(files)
        # TODO: ignored_paths: dict[str, dict] = group_by_paths(ignored)
        # TODO: filtered_paths: dict[str, dict] = group_by_paths(filtered)

        paired_results: list[dict] = []
        paired_extentions = {}
        paired_images: dict = {}
        unpaired_extentions = {}

        # Seperate paired and unpaired files by path.
        for path, ext in files_paths.items():
            if len(ext.keys()) == 2:
                paired_extentions[path] = ext
                for extention_file in ext.values():
                    paired_images[extention_file['file_name']] = extention_file
            else:
                unpaired_extentions[path] = ext

        if not paired_extentions:
            list_files('[RAW+] -> No paired files!', files, ignored + filtered)

        paired_results = self.__master_and_copies_RAWplus_paired(moment, paired_extentions)

        # Called after Paired to be able to match to paired
        matched_copies = []
        unmatched = []
        if unpaired_extentions:
            # Index checksums to copies
            paired_checksums = self.__paired_checksums(paired_results, files)

            for extention in unpaired_extentions.values():
                for file in extention.values():
                    checksum = file['checksum']
                    ext = file['file_extention']
                    path = file['file_path']
                    found = False
                    if checksum in paired_checksums.keys():
                        for r in paired_results:
                            if r['master'] == paired_checksums[checksum]['master']:
                                # paired_checksums[checksum]['copies'].append(path)
                                r['copies'].append(path)
                                found = True
                                break
                    if found:
                        matched_copies.append(file)
                    else:
                        unmatched.append(file)

            if unmatched:
                # TODO: Match with image name
                #
                list_files(
                    f"[RAW+]\tMoment: {moment}\t Unpaired, No matching checksums",
                    [file for path, extentions in paired_extentions.items() for file in extentions.values()] + matched_copies,
                    # [file for path, extentions in unpaired.items() for file in extentions.values()]
                    unmatched
                )

            # self._RAW_plus_unpaired(moment, unpaired, paired_checksums)

            # list_files(f'[Extentions] {moment} - singles', singles)
            #  Do I need to deal with
            # TODO:
            # results self._RAW_plus_unpaired(singles)
            # pprint([
            #     file
            #     for file in extention.values()
            #     for path, extentions in unpaired.items()
            # ])
            # pass

        if not paired_results:
            list_files('[RAW+] -> No paired results!', files, ignored + filtered)

        elif ignored or filtered:
            for file in ignored:
                file_image = file['file_name']
                if file_image in paired_images.keys():
                    # first item in array is RAW
                    paired_results[0]['ignored'].append(file['file_path'])
                else:
                    print('[RAW+] Ignored not in paired extentions', file_image, list(paired_images.keys()))
                    list_files('[RAW+] - Ignored not matching paired', files, ignored)
                    pprint(paired_extentions)

            for file in filtered:
                file_image = file['file_name']
                if file_image in paired_images.keys():
                    # first item in array is RAW
                    paired_results[0]['filtered'].append(file['file_path'])
                else:
                    print('[RAW+] Filtered not in paired extentions', file_image, list(paired_images.keys()))
                    list_files('[RAW+] - Filtered not matching paired', files, filtered)

        if not unpaired_extentions and not paired_extentions:
            self.LOGGER.error('[RAW+] -> Expeced Singels or Paired, Neither found for {moment}')
            list_files(f'[Extentions] {moment} - NOT singles and NOT paired', files)

        return paired_results

    def __paired_checksums(self, paired_results: list, files: list) -> dict:
        paired_checksums = {}
        for r in paired_results:
            for f in files:
                if f['file_path'] == r['master']:
                    paired_checksums[f['checksum']] = {
                        'master': r['master'],
                        'copies': r['copies']
                    }
        return paired_checksums

    def __sequence(self, camera, moment, moment_files: list, ignored_files: list = [], filtered_files: list = []) -> list:
        # We will recall proccess_camera_moment_files for each step in a sequcence for the moment
        results: list[dict] = []

        # Index ignored by image
        image_ignored: dict[str, list] = {}
        for i in ignored_files:
            image = i['file_name']
            image_ignored[image] = image_ignored.get(image, []) + [i]

        # Index filtered by images
        image_filtered: dict[str, list] = {}
        for f in filtered_files:
            image = f['file_name']
            image_filtered[image] = image_filtered.get(image, []) + [f]

        # Group by image and checksums
        moment_images: dict = {}
        # moment_checksums = {}
        # moment_extentions = {}
        for m in moment_files:
            image = m['file_name']
            moment_images[image] = moment_images.get(image, []) + [m]
            # moment_checksums[m['checksum']] = moment_images.get(m['checksum'], []) + [m]
            # moment_extentions[m['file_extention']] = moment_images.get(m['file_extention'], []) + [m]

        # if not len(moment_checksums) == len(moment_images):
        #     # TODO: Possibly not a sequence ?
        #     message = f"[{camera}]\tMoment: {moment}\t Multiple Names and Multiple Checksums -- Not a Sequences ??"
        #     list_files(message, moment_files, ignored_files + filtered_files)
        # else:

        for step in list(moment_images.keys()):
            step_files = moment_images[step]
            step_ignored: list = []
            step_filtered: list = []
            images_in_step: dict[str, list] = {}
            checksums_in_step: dict[str, list] = {}
            extentions_in_step: dict[str, list] = {}

            for f in step_files:
                images_in_step[f['file_name']] = images_in_step.get(f['file_name'], []) + [f]
                checksums_in_step[f['checksum']] = checksums_in_step.get(f['checksum'], []) + [f]
                extentions_in_step[f['file_extention']] = extentions_in_step.get(f['file_extention'], []) + [f]

            if len(images_in_step) > 1:
                print("[Sequence] -> Many images in step")
                print(list(images_in_step.keys()))

            for image in images_in_step.keys():
                if image in image_ignored.keys():
                    step_ignored = step_ignored + image_ignored[image]
                    del image_ignored[image]

                if image in image_filtered.keys():
                    step_filtered = step_filtered + image_filtered[image]
                    del image_filtered[image]

            # TODO: Match on checksums
            for checksum in checksums_in_step.keys():
                for image, image_ignored_files in image_ignored.items():
                    updated_ignore_list = []
                    for file_info in image_ignored_files:
                        if file_info['checksum'] not in checksums_in_step.keys():
                            updated_ignore_list.append(file_info)
                        else:
                            print(image)

            # for image, image_ignored_files in image_ignored.items():
            #     if image in images_in_step.keys():
            #         step_ignored = step_ignored + image_ignored[image]
            #         del image_ignored[image]

            #     else:
            #         for file in image_ignored_files:
            #             if file['checksum'] in checksums_in_step:
            #                 # print(image)
            #                 step_ignored = step_ignored + [file]
            #                 # del image_ignored[image]
            #                 # break

            # if image_filtered:
            #     image = list(images_in_step)[0]

            #     if image in image_filtered.keys():
            #         step_filtered = step_filtered + image_filtered[image]
            #         del image_filtered[image]

                # TODO: match on checksums

            results = results + self.process_moment(camera, moment, step_files, step_ignored, step_filtered)

        if image_ignored:
            print('[Sequence] -> Unmatched Ignored', list(image_ignored.keys()))
            list_files(f"[{camera}]\tMoment: {moment}\t [Sequence] -> Ignored need to be included", moment_files, ignored_files)

        if image_filtered:
            print('[Sequence] -> Unmatched Filtered', list(image_filtered.keys()))
            list_files(f"[{camera}]\tMoment: {moment}\t [Sequence] -> Filtered need to be included", moment_files, filtered_files)

        return results

    def __master_and_copies(
        self,
        files: list,
        copies: list = [],
        ignored: list = [],
        filtered: list = [],
        unresolved: list = []
    ) -> dict:
        image_master_file: str = ''
        image_copies: list = []
        image_unresolved: list = []

        if len(files) == 1:
            f = files[0]
            image_master_file = f['file_path']
            self.LOGGER.info('[Single file] %s', image_master_file)

        else:
            image_master_file = self.__prefered_master(files)
            if not image_master_file:
                # list_files('No Prefered Master', files, ignored + filtered)
                image_unresolved = [f['file_path'] for f in files]

            else:
                #  Exclude Master from list of files to be copies
                image_copies = [
                    f['file_path']
                    for f in files
                    if f['file_path'] != image_master_file
                ]

        return {
            'master': image_master_file,
            'copies': copies + image_copies,
            'ignored': [f['file_path'] for f in ignored],
            'filtered': [f['file_path'] for f in filtered],
            'unresolved': [f['file_path'] for f in unresolved] + image_unresolved
        }

    def __master_and_copies_RAWplus_paired(self, moment: str, paired: dict) -> list:
        results = []
        if paired:
            checksums = group_by_raw_plus_checksums(paired)
            raw = checksums['raw']
            jpg = checksums['jpg']

            if len(raw) == 1 and len(jpg) == 1:
                results.append(self.__master_and_copies(list(raw.values())[0]))
                results.append(self.__master_and_copies(list(jpg.values())[0]))

            else:
                self.LOGGER.error(f'[RAW+] -> Paired have multiple checksums for {moment}')
                print(f'[RAW+] -> Paired have multiple checksums for {moment}')
                # print('paired')
                # pprint(paired)
                # print('checksums')
                # pprint(checksums)

        return results

    def __prefered_master(self, files: list) -> str:
        """Identify a master image file"""
        image_master_file = ''

        for preferred in self.preferred['paths']:
            if image_master_file:
                break

            for f in files:
                path = f['file_path']
                # TODO: Preference camera file names
                # TODO: Have disabled ignore copies
                # if f['copy']:
                #     continue  # Ignore copies

                if preferred in path:
                    image_master_file = path
                    break

        if not image_master_file:
            self.LOGGER.error('[Prefered Master] - No master file identified')
            pass

        return image_master_file

    def __camera_extention(self, camera: str, condition: str = "extentions"):
        extentions = []

        if camera not in self.camera_rules:
            self.LOGGER.error('[Configuration] - Camera not found in "cleanup.camera_rules"')
        else:
            # collect Rules
            for filter in self.camera_rules[camera].get('filters', []):
                if filter['condition'] == condition:
                    extentions.append(filter['matches'])
        return extentions
