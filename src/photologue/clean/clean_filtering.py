from typing import TypedDict


class FilterRules(TypedDict):
    paths: list[str]
    files: list[str]


class CameraCondition(TypedDict, total=False):
    condition: str
    matches: set | None
    action: str
    file_props: dict


CameraFilters = list[CameraCondition]


class Camera(TypedDict, total=False):
    # Owner: str
    # Location: str
    # Action Steps: Check Dropbox for duplicates
    # Notes: str
    filters: CameraFilters


CameraRules = dict[str, Camera]


def filter_camera_files(camera_rules: Camera, condition: str, matches: str | None, files: list) -> dict:
    rules = []
    results: dict = {
        'keep': [],
        'ignore': []
    }

    # if camera not in camera_rules:
    #     logger.error('[Configuration] - Camera not found in "cleanup.camera_rules"')
    # else:

    # collect Rules
    for filter_on in camera_rules.get('filters', []):
        if filter_on['condition'] == condition and filter_on['matches'] == matches:
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
                for key, value in rule.get('file_props', {}).items():
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
                    for key, value in rule.get('file_props', {}).items():
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


# returns the filtered files
def filter_out(camera_filters: CameraFilters, file: dict) -> bool:
    keep = False
    ignore = False

    if not camera_filters:
        return True

    for rule in camera_filters:
        if rule['action'] == 'keep':
            rule_holds = True
            for key, value in rule['file_props'].items():
                if file[key] != value:
                    rule_holds = False
                    break
            if rule_holds:
                keep = True
                break

    if not keep:
        # Remove any ignore rules instead
        for rule in camera_filters:
            if rule['action'] == 'ignore':
                rule_holds = True
                for key, value in rule['file_props'].items():
                    if file[key] != value:
                        rule_holds = False
                        break
                if rule_holds:
                    ignore = True
                    # return False

    if not keep and not ignore:
        # Nothing filtered -> Everything kept
        return True
    elif keep:
        #  Only keep file that satisfies the first rule thats true
        return True
    elif ignore:
        # We know what to ignore, what is left we'll keep
        return False
    else:
        return True


def ignore_file(ignore_rules: FilterRules, file_path: str) -> bool:
    ignore = False

    if file_path in ignore_rules.get('files', []):
        ignore = True
    elif ignore_rules.get('paths'):
        for path in ignore_rules['paths']:
            if path in file_path:
                ignore = True

    return ignore
