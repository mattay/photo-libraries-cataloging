def original_date(date_time: str) -> object:
    date = '    :  :  '
    if date_time == '-':
        pass
    elif date_time == '    :  :     :  :':
        pass
    elif date_time:
        date = date_time[:10]
    return date


def file_add_props(file: dict) -> dict:
    # clean up dates
    file['image_date'] = original_date(file['date_time_original'])
    file['mod_date'] = original_date(file['date_time_modifed'])
    # Calculate if file has been modified
    file['modified'] = 1 if file['image_date'] != file['mod_date'] else 0
    file['copy'] = 1 if file['has_copy_in_subfix'] or file['has_copy_in_name'] else 0

    return file


def group_image_creation(files: list[dict]) -> dict:
    collected: dict[str, list] = {}

    for file in files:
        creation = file['date_time_original']
        values = collected.get(creation, [])
        values.append(file)
        collected[creation] = values

    return collected


def group_undefined_moments(files: list[dict]) -> dict:
    collected: dict[str, list] = {}

    sorted_files = sorted(files, key=lambda x: x['file_name'])

    idx = 0
    while sorted_files:
        looking_for_images = set()
        looking_for_checksums = set()

        file_a = sorted_files.pop()
        looking_for_images.add(file_a['file_name'])
        looking_for_checksums.add(file_a['checksum'])

        collected[f'{idx}'] = [file_a]

        while looking_for_images or looking_for_checksums:
            image = looking_for_images.pop() if looking_for_images else None
            checksum = looking_for_checksums.pop() if looking_for_checksums else None

            unmatched = []
            while sorted_files:
                match = False
                file_b = sorted_files.pop()

                if file_b['file_name'] == image:
                    match = True
                    if file_b['checksum'] != checksum:
                        # Adding checksum
                        looking_for_checksums.add(file_b['checksum'])

                elif file_b['checksum'] == checksum:
                    match = True
                    if file_b['file_name'] != image:
                        # Adding image
                        looking_for_images.add(file_b['file_name'])

                if not match:
                    unmatched.append(file_b)

                else:
                    collected[f'{idx}'] = collected.get(f'{idx}', []) + [file_b]

            # Rebuild sorted_files
            sorted_files = unmatched

        idx += 1

    return collected
