import os
from os.path import splitext

import re


RE_FILE_IS: dict = {
    # DISCARD
    'temp': re.compile(r"^\.", re.IGNORECASE),
    'thumb': re.compile(r"^.humb_", re.IGNORECASE),
    'face': re.compile(r".*_face[0-9]+$", re.IGNORECASE),
    '_n': re.compile(r".*_n$", re.IGNORECASE),
    # KEEP
    'copy_of': re.compile(r"^Copy (\([1-9]\) )?of ", re.IGNORECASE),
    'copy': re.compile(r".*(_[1-9])+$", re.IGNORECASE),
    'duplicate': re.compile(r".* \([1-9]\)$", re.IGNORECASE),
    'double_extention': re.compile(r".*\..{3}$", re.IGNORECASE),
}

RE_LIBRARY: dict = {
    'aplibrary': re.compile(r"(?P<library_path>.*/(?P<library_name>.+)\.aplibrary)/(?P<is>\w+)/"),
    'apvault': re.compile(r"(?P<library_path>.*/(?P<library_name>.+)\.apvault)/(?P<is>\w+)/"),
    'iphoto': re.compile(r"(?P<library_path>.*/(?P<library_name>iPhoto Library( #\d)?))/(?P<is>(s)?\w+)/"),
    'photoslibrary': re.compile(r"(?P<library_path>.*/(?P<library_name>.+)\.photo(s)?library)/(?P<is>(s)?\w+)/"),
    'photoslibraryProxies': re.compile(r"(?P<library_path>.*/(?P<library_name>.+)\.photo(s)?library)/resources/(?P<is>proxies)/"),
    'lrlibrary': re.compile(r"(?P<library_path>.*/(?P<library_name>.+)\.lrlibrary/.*)/(?P<is>originals)/"),
    'lightroom': re.compile(r"(?P<library_path>.*/(?P<library_name>Lightroom( \w+)?)/.*)/(?P<is>originals)/"),
}


def clean_name(image):
    global RE_FILE_IS
    base_name = os.path.basename(image)
    name, ext = splitext(base_name)
    image_name = {
        'name': name,
        'path': image,
        'extention': ext,
        'thumbnail': False,
        'copy in name': False,
        'copy subfix': False,
        'face': False,
        'temp': False,
    }

    # DISCARD - Don't clean up
    if RE_FILE_IS['temp'].match(name):
        image_name['temp'] = True

    if RE_FILE_IS['_n'].match(name):
        image_name['temp'] = True

    if RE_FILE_IS['thumb'].match(name):
        image_name['thumbnail'] = True

    if RE_FILE_IS['face'].match(name):
        image_name['face'] = True

    # KEEP
    if RE_FILE_IS['copy_of'].match(name):
        name = RE_FILE_IS['copy_of'].sub('', name)
        image_name['copy in name'] = True

    if RE_FILE_IS['copy'].match(name):
        name = re.sub(r'(_[1-9])+$', '', name)
        image_name['copy subfix'] = True

    if RE_FILE_IS['duplicate'].match(name):
        name = re.sub(r' \([1-9]\)$', '', name)
        image_name['copy subfix'] = True

    if RE_FILE_IS['double_extention'].match(name):
        name = re.sub(r'\..{3}$', '', name)

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

    aplibrary = RE_LIBRARY['aplibrary'].match(path)
    apvault = RE_LIBRARY['apvault'].match(path)
    iphoto = RE_LIBRARY['iphoto'].match(path)
    photoslibrary = RE_LIBRARY['photoslibrary'].match(path)
    photoslibraryProxies = RE_LIBRARY['photoslibraryProxies'].match(path)
    lrlibrary = RE_LIBRARY['lrlibrary'].match(path)
    lightroom = RE_LIBRARY['lightroom'].match(path)

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
