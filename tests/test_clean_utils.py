import pytest
from photologue.clean.clean_utils import are_files_incrementing


@pytest.mark.parametrize("paths, expected", [
    ([
        {'file_name': 'G0010006', 'file_path': '/Volumes/Jedi/GoPro/2014-01-02 Home/HERO4 Silver/PHOTO_SEQUENCE 1/G0010006.JPG'},
        {'file_name': 'G0010007', 'file_path': '/Volumes/Jedi/GoPro/2014-01-02 Home/HERO4 Silver/PHOTO_SEQUENCE 1/G0010007.JPG'}
    ], True),
    ([
        {'file_name': '_IGP0671', 'file_path': '/Volumes/LaCie/_MASTER_Aperture_20190520/Brisbane.aplibrary/Masters/2011/01/13/20110113-103404/_IGP0671.PEF'},
        {'file_name': '_IGP0672', 'file_path': '/Volumes/LaCie/_MASTER_Aperture_20190520/Brisbane.aplibrary/Masters/2011/01/13/20110113-103404/_IGP0672.PEF'}
    ], True)
])
def test__are_files_incrementing(paths, expected):
    assert are_files_incrementing(paths) == expected
