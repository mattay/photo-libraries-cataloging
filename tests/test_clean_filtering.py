import pytest
from photologue.clean.clean_filtering import (
    # filter_camera_files,
    filter_out,
    ignore_file
)

cleanup_rules = {
    'preferred': {
        'paths': [],
        'files': []
    },
    'ignore': {
        'paths': [
            '/Volumes/Padawan/_Pictures/_Exports/AMATA2009/'
        ],
        'files': [
           '/Volumes/Padawan/_Pictures/_Exports/bostonTaxi.JPG'
        ]
    },
    'camera_rules': {
        'Canon DIGITAL IXUS 500': {
            'filters': [{
                'condition': 'names',
                'matches': None,
                'action': 'ignore',
                'file_props': {
                    'file_name': 'old_& _new_rocker_covers'
                }
            }]
        }
    }
}

files = [
    {
        # "camera_model": "Canon DIGITAL IXUS 500",
        # "date_time_original": "2005:04:09 17:41:06",
        # "date_time_modifed": "2008:04:14 18:26:38+10:00",
        "file_name": "old_& _new_rocker_covers",
        # "checksum": "2585595678",
        # "size": 173466,
        # "file_extention": ".JPG",
        # "has_copy_in_subfix": 0,
        # "has_copy_in_name": 0,
        "file_path": "/Volumes/Jedi/CLEANUP/Cars/2010/03/12/20100312-225618/old_& _new_rocker_covers.JPG",
        # "quality": "Fine",
        # "software": None,
        # "color_space": "sRGB",
        # "library_type": None,
        # "library_name": None,
        # "library_path": None
    }
]

# TODO:
# filter_camera_files

@pytest.mark.parametrize("camera_filters, file, expected", [
    (cleanup_rules['camera_rules']['Canon DIGITAL IXUS 500']['filters'], files[0], False)
])
def test__filter_for(camera_filters, file, expected):
    assert filter_out(camera_filters, file) == expected


@pytest.mark.parametrize("ignore_rules, file_path, expected", [
    (cleanup_rules['ignore'], '/Volumes/Padawan/_Pictures/_Exports/bostonTaxi.JPG', True),
    (cleanup_rules['ignore'], '/Volumes/Padawan/_Pictures/_Exports/IMGP8402-20110430.JPG',  False),
    (cleanup_rules['ignore'], '/Volumes/Padawan/_Pictures/_Exports/AMATA2009/P1010142.RW2', True),
])
def test__ignore_file(ignore_rules, file_path, expected):
    assert ignore_file(ignore_rules, file_path, ) == expected
