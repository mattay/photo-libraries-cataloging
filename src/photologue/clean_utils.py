
import os


def group_by_paths(files: list) -> dict[str, dict]:
    """
    Looking for raw files with matching jpeg file in same directory
    """
    paths: dict[str, dict] = {}

    for f in files:
        dir = os.path.dirname(f['file_path'])
        d = paths.get(dir, {})
        d[f.get('file_extention')] = f
        paths[dir] = d

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


def list_files(group: str, files: list):
    print(group)
    print("  DATE       MOD DATE   M CHECKSUM     C SOFTWARE         QUALITY  COLOURSPACE  FILE PATH")
    print("  ---------- ---------- - ------------ - ---------------- -------- ------------ ------------------------------------------------")
    [print(f"  {file['image_date']} {file['mod_date']} {file['modified']} {file['checksum']:>12} {file['copy']}" +
           f" {str(file['software']):<16} {str(file['quality']):<8} {str(file['color_space']):<12} {file['file_path']}")
        for file
        in sorted(files, key=lambda d: d['checksum'])
     ]
