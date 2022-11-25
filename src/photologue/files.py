import os
from os.path import splitext

# import logging
import re
# from pprint import pprint


def clean_name(image):
    base_name = os.path.basename(image)
    name, ext = splitext(base_name)
    image_name = {
        'name': name,
        'path': image,
        'extention': ext,
        'thumbnail': False,
        'copy in name': False,
        'copy subfix': False,
        'face': False
    }

    is_thumb = re.compile(r"^thumb_", re.IGNORECASE)
    is_copy_of = re.compile(r"^Copy (\([1-9]\) )?of ", re.IGNORECASE)
    is_face = re.compile(r".*_face[0-9]+$", re.IGNORECASE)
    is_copy = re.compile(r".*(_[1-9])+$", re.IGNORECASE)
    is_duplicate = re.compile(r".* \([1-9]\)$", re.IGNORECASE)

    if is_thumb.match(name):
        name = is_thumb.sub('', name)
        image_name['thumbnail'] = True

    if is_copy_of.match(name):
        name = is_copy_of.sub('', name)
        image_name['copy in name'] = True

    if is_copy.match(name):
        name = re.sub(r'(_[1-9])+$', '', name)
        image_name['copy subfix'] = True

    if is_face.match(name):
        name = re.sub(r'_face[0-9]+$', '', name)
        image_name['face'] = True

    if is_duplicate.match(name):
        name = re.sub(r' \([1-9]\)$', '', name)
        image_name['copy subfix'] = True

    image_name['name'] = name

    return image_name


def library(path):
    library = {
        'library_type': None,
        'library_name': None,
        'library_path': None,
        'is': None,
        'is_master': False,
        'is_preview': False,
        'is_thumbnail': False,
        'is_proxy': False
    }

    aplibrary = re.match(r"(?P<library_path>.*/(?P<library_name>.+)\.aplibrary)/(?P<is>\w+)/", path)
    apvault = re.match(r"(?P<library_path>.*/(?P<library_name>.+)\.apvault)/(?P<is>\w+)/", path)

    iphoto = re.match(r"(?P<library_path>.*/(?P<library_name>iPhoto Library( #\d)?))/(?P<is>(s)?\w+)/", path)

    photoslibrary = re.match(r"(?P<library_path>.*/(?P<library_name>.+)\.photo(s)?library)/(?P<is>(s)?\w+)/", path)
    photoslibraryProxies = re.match(r"(?P<library_path>.*/(?P<library_name>.+)\.photo(s)?library)/resources/(?P<is>proxies)/", path)

    lrlibrary = re.match(r"(?P<library_path>.*/(?P<library_name>.+)\.lrlibrary/.*)/(?P<is>originals)/", path)
    lightroom = re.match(r"(?P<library_path>.*/(?P<library_name>Lightroom( \w+)?)/.*)/(?P<is>originals)/", path)

    if aplibrary:
        library['library_type'] = "aplibrary"
        library['library_name'] = aplibrary.group('library_name')
        library['library_path'] = aplibrary.group('library_path')

        is_image_type = f'is_{aplibrary.group("is").rstrip("s").lower()}'
        library['is'] = is_image_type
        library[is_image_type] = True

    elif apvault:
        library['library_type'] = "apvault"
        library['library_name'] = apvault.group('library_name')
        library['library_path'] = apvault.group('library_path')
        is_image_type = f'is_{apvault.group("is").rstrip("s").lower()}'
        library['is'] = is_image_type
        library[is_image_type] = True

    elif iphoto:
        library['library_type'] = "iphoto"
        library['library_name'] = iphoto.group('library_name')
        library['library_path'] = iphoto.group('library_path')
        is_image_type = f'is_{iphoto.group("is").rstrip("s").lower()}'
        library['is'] = is_image_type
        library[is_image_type] = True

    elif photoslibrary:
        library['library_type'] = "photoslibrary"
        library['library_name'] = photoslibrary.group('library_name')
        library['library_path'] = photoslibrary.group('library_path')
        is_image_type = f'is_{photoslibrary.group("is").rstrip("s").lower()}'
        if photoslibraryProxies:
            is_image_type = "is_proxy"
        library['is'] = is_image_type
        library[is_image_type] = True

    elif lrlibrary:
        library['library_type'] = "lrlibrary"
        library['library_name'] = lrlibrary.group('library_name')
        library['library_path'] = lrlibrary.group('library_path')
        is_image_type = f'is_{lrlibrary.group("is").rstrip("s").lower()}'
        library['is'] = is_image_type
        library[is_image_type] = True

    elif lightroom:
        library['library_type'] = "lightroom"
        library['library_name'] = lightroom.group('library_name')
        library['library_path'] = lightroom.group('library_path')

        lib_type = lightroom.group("is").rstrip("s").lower()
        lib_type = "master" if lib_type == "original" else lib_type
        is_image_type = f'is_{lib_type}'
        library['is'] = is_image_type
        library[is_image_type] = True

    else:
        pass
        # TODO: Log as warning
        # print('UNKNOWEN library type', path)

    return library
