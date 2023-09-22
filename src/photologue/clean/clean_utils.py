import re


def are_files_incrementing(files: list, increment=1) -> bool:
    unique_names = list(set([
        file['file_name']
        for file in files]
    ))
    if len(unique_names) < 2:
        return False

    image_numbers = []
    for file in unique_names:
        match = re.search(r'\d+', file)
        # if not match:
        #     return False
        if match:
            image_numbers.append(int(match.group()))

    # Check if the numbers are incrementing by {increment}
    image_numbers.sort()
    increment_seen = False
    for i in range(len(image_numbers) - 1):
        if image_numbers[i] + increment == image_numbers[i + 1]:
            increment_seen = True
            # return False

    return increment_seen


def list_files(group: str, files: list, secondary_files: list = []) -> None:
    print(group)
    print(" DATE       MOD DATE   M CHECKSUM     SIZE         C SOFTWARE         QUALITY  LIB TYPE       FILE PATH")
    print(" ========== ========== = ============ ============ = ================ ======== ============== " + "="*100)
    [print(f" {file['image_date']} {file['mod_date']} {file['modified']} {file['checksum']:>12} {file['size']:>12} {file['copy']}" +
           f" {str(file['software']):<16} {str(file['quality']):<8} {str(file['library_type']):<14} {file['file_path']}")
        for file
        in sorted(files, key=lambda d: d['checksum'])
     ]
    if secondary_files:
        print(" ---------- ---------- - ------------ ------------ - ---------------- -------- -------------- " + "-"*100)
        [print(f" {file['image_date']} {file['mod_date']} {file['modified']} {file['checksum']:>12} {file['size']:>12} {file['copy']}" +
               f" {str(file['software']):<16} {str(file['quality']):<8} {str(file['library_type']):<14} {file['file_path']}")
            for file
            in sorted(secondary_files, key=lambda d: d['checksum'])
         ]
    print()
