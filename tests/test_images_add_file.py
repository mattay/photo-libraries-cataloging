import pytest
from photologue.images import Images


@pytest.fixture
def images():
    return Images(
        ':memory:',
        [],
        {'preferred': {}, 'ignore': {}, 'camera_rules': {}},
    )


@pytest.mark.parametrize("path, expected_name, expected_subfix, expected_library_type, expected_library_name", [
    (
        '/Volumes/Jedi/CLEANUP/Cars/2010/03/13/20100313-083911/IMG_1740 (1).jpg',
        'IMG_1740',
        True,
        None,
        None,
    ),
])
def test__add_file_standalone(images, path, expected_name, expected_subfix, expected_library_type, expected_library_name):
    result = images.add_file(path)
    assert result == path

    files = images.CATALOGUE.files()
    assert len(files) == 1
    assert files[0] == path


@pytest.mark.parametrize("path, expected_library_type, expected_library_name", [
    (
        '/Volumes/LaCie/_MASTER_Aperture_20190520/Travels.aplibrary/Masters/2009/02/10/20090210-225917/_IGP2852.JPG (1).JPG',
        'aplibrary',
        'Travels',
    ),
])
def test__add_file_aperture_master(images, path, expected_library_type, expected_library_name):
    result = images.add_file(path)
    assert result == path

    files = images.CATALOGUE.files()
    assert len(files) == 1
    assert files[0] == path


@pytest.mark.parametrize("path", [
    '/Volumes/Padawan/_Pictures/Aperture Library Collections/_Libraries/Aperture Library__1.aplibrary/Previews/2011/01/17/20110117-164607/2CZ5vdr2RwqvD0lwTV6+kw/IMGP7419.jpg',
])
def test__add_file_rejects_preview(images, path):
    result = images.add_file(path)
    assert result is None

    files = images.CATALOGUE.files()
    assert len(files) == 0


@pytest.mark.parametrize("path", [
    '/Volumes/Padawan/_Pictures/_Backups/Apeture_Import_Backups/2014_SouthAmerica /20150119/.__IGP8686.PEF',
])
def test__add_file_rejects_temp(images, path):
    result = images.add_file(path)
    assert result is None

    files = images.CATALOGUE.files()
    assert len(files) == 0


@pytest.mark.parametrize("path", [
    '/Volumes/Padawan/_Pictures/_Libaries/iPhoto Library #4/Thumbnails/2012/06/05/20120605-235330/_IGP6908_face0.jpg',
])
def test__add_file_rejects_face(images, path):
    result = images.add_file(path)
    assert result is None

    files = images.CATALOGUE.files()
    assert len(files) == 0
