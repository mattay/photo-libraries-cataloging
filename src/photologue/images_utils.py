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


def group_files_by_image_date(files: list[dict]) -> dict:
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

    for file in files:
         # Add to Hhiarchy
        i = collected.get(file['file_name'], {})
        t = i.get(file['image_date'], [])
        t.append(file)

        i[file['image_date']] = t
        collected[file['file_name']] = i

    return collected
