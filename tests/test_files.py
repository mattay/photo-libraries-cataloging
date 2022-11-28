import pytest
from photologue.files import clean_name


@pytest.mark.parametrize("test__file_paths, expected_image_name", [
    ('/Volumes/Jedi/CLEANUP//Cars/2010/03/13/20100313-083911/IMG_1740 (1).jpg', {
        'name': 'IMG_1740',
        'path': '/Volumes/Jedi/CLEANUP//Cars/2010/03/13/20100313-083911/IMG_1740 (1).jpg',
        'extention': '.jpg',
        'thumbnail': False,
        'copy in name': False,
        'copy subfix': True,
        'face': False
    })
])
def test__clean_name(test__file_paths, expected_image_name):
    assert clean_name(test__file_paths) == expected_image_name
