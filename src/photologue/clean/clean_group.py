import os
from os.path import splitext


def group_by_paths(files: list) -> dict[str, dict[str, dict]]:
    """
    Looking for raw files with matching jpeg file in same directory
    """
    paths: dict[str, dict[str, dict]] = {}

    for file in files:
        dir = os.path.dirname(file['file_path'])
        base_name = os.path.basename(file['file_path'])
        name, ext = splitext(base_name)
        # Append file name to path to account for sequence images for a moment
        path = f"{dir}/{name}"
        path_files = paths.get(path, {})
        path_files[file['file_extention']] = file
        paths[path] = path_files

    return paths


def group_by_checksum(files: list, filter_out_tag: str = '') -> dict[str, list]:
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


def group_by_raw_plus_checksums(paired: dict) -> dict[str, dict]:
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
