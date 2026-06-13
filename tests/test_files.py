import pytest
from photologue.files.files import clean_name, extract_library, is_desired


files = {
    '/Volumes/Jedi/CLEANUP//Cars/2010/03/13/20100313-083911/IMG_1740 (1).jpg': {
        'file_path': '/Volumes/Jedi/CLEANUP//Cars/2010/03/13/20100313-083911/IMG_1740 (1).jpg',
        'image_name': {
            'name': 'IMG_1740',
            'path': '/Volumes/Jedi/CLEANUP//Cars/2010/03/13/20100313-083911/IMG_1740 (1).jpg',
            'extention': '.jpg',
            'thumbnail': False,
            'copy in name': False,
            'copy subfix': True,
            'face': False,
            'temp': False
        },
        'library': {
            'library_type': '',
            'library_name': '',
            'library_path': '',
            'is': '',
            'is_master': False,
            'is_preview': False,
            'is_thumbnail': False,
            'is_proxy': False
        },
        'desired': True
    },
    '/Volumes/Jedi/ApertureLibraryBackups/cars/BF Sedan/P1010913 (1).JPG': {
        'file_path': '/Volumes/Jedi/ApertureLibraryBackups/cars/BF Sedan/P1010913 (1).JPG',
        'image_name': {
            'name': 'P1010913',
            'path': '/Volumes/Jedi/ApertureLibraryBackups/cars/BF Sedan/P1010913 (1).JPG',
            'extention': '.JPG',
            'thumbnail': False,
            'copy in name': False,
            'copy subfix': True,
            'face': False,
            'temp': False
        },
        'library': {
            'library_type': '',
            'library_name': '',
            'library_path': '',
            'is': '',
            'is_master': False,
            'is_preview': False,
            'is_thumbnail': False,
            'is_proxy': False
        },
        'desired': True
    },
    # Library - apvault
    '/Volumes/Padawan/_Pictures/_Backups/Vaults/Travels_src_LaCaie.apvault/Masters/2010/05/23/20100523-143032/IMGP1315.PEF': {
        'file_path': '/Volumes/Padawan/_Pictures/_Backups/Vaults/Travels_src_LaCaie.apvault/Masters/2010/05/23/20100523-143032/IMGP1315.PEF',
        'image_name': {
            'name': 'IMGP1315',
            'path': '/Volumes/Padawan/_Pictures/_Backups/Vaults/Travels_src_LaCaie.apvault/Masters/2010/05/23/20100523-143032/IMGP1315.PEF',
            'extention': '.PEF',
            'thumbnail': False,
            'copy in name': False,
            'copy subfix': False,
            'face': False,
            'temp': False
        },
        'library': {
            'library_type': 'apvault',
            'library_name': 'Travels_src_LaCaie',
            'library_path': '/Volumes/Padawan/_Pictures/_Backups/Vaults/Travels_src_LaCaie.apvault',
            'is': 'is_master',
            'is_master': True,
            'is_preview': False,
            'is_thumbnail': False,
            'is_proxy': False
        },
        'desired': True
    },
    # Library - iphoto
    '/Volumes/Padawan/_Pictures/_Libaries/iPhoto Library/Masters/2009/Eksitis Chrismas Party 2009/_IGP5200.DNG': {
        'file_path': '/Volumes/Padawan/_Pictures/_Libaries/iPhoto Library/Masters/2009/Eksitis Chrismas Party 2009/_IGP5200.DNG',
        'image_name': {
            'name': '_IGP5200',
            'path': '/Volumes/Padawan/_Pictures/_Libaries/iPhoto Library/Masters/2009/Eksitis Chrismas Party 2009/_IGP5200.DNG',
            'extention': '.DNG',
            'thumbnail': False,
            'copy in name': False,
            'copy subfix': False,
            'face': False,
            'temp': False
        },
        'library': {
            'library_type': 'iphoto',
            'library_name': 'iPhoto Library',
            'library_path': '/Volumes/Padawan/_Pictures/_Libaries/iPhoto Library',
            'is': 'is_master',
            'is_master': True,
            'is_preview': False,
            'is_thumbnail': False,
            'is_proxy': False,
        },
        'desired': True
    },
    # Library - lightroom
    '/Volumes/Padawan/_Pictures/_Libaries/Lightroom/Lightroom CC/8c5bbdf7cd854e48a842a773b59c6d51/originals/2019/2019-08-10/IMG_4545.JPG': {
        'file_path': '/Volumes/Padawan/_Pictures/_Libaries/Lightroom/Lightroom CC/8c5bbdf7cd854e48a842a773b59c6d51/originals/2019/2019-08-10/IMG_4545.JPG',
        'image_name': {
            'name': 'IMG_4545',
            'path': '/Volumes/Padawan/_Pictures/_Libaries/Lightroom/Lightroom CC/8c5bbdf7cd854e48a842a773b59c6d51/originals/2019/2019-08-10/IMG_4545.JPG',
            'extention': '.JPG',
            'thumbnail': False,
            'copy in name': False,
            'copy subfix': False,
            'face': False,
            'temp': False
        },
        'library': {
            'library_type': 'lightroom',
            'library_name': 'Lightroom CC',
            'library_path': '/Volumes/Padawan/_Pictures/_Libaries/Lightroom/Lightroom CC/8c5bbdf7cd854e48a842a773b59c6d51',
            'is': 'is_master',
            'is_master': True,
            'is_preview': False,
            'is_thumbnail': False,
            'is_proxy': False
        },
        'desired': True
    },
    # Library - aplibrary
    # Image Name - _IGP2852.JPG (1).JPG
    '/Volumes/LaCie/_MASTER_Aperture_20190520/Travels.aplibrary/Masters/2009/02/10/20090210-225917/_IGP2852.JPG (1).JPG': {
        'file_path': '/Volumes/LaCie/_MASTER_Aperture_20190520/Travels.aplibrary/Masters/2009/02/10/20090210-225917/_IGP2852.JPG (1).JPG',
        'image_name': {
            'name': '_IGP2852',
            'path': '/Volumes/LaCie/_MASTER_Aperture_20190520/Travels.aplibrary/Masters/2009/02/10/20090210-225917/_IGP2852.JPG (1).JPG',
            'extention': '.JPG',
            'thumbnail': False,
            'copy in name': False,
            'copy subfix': True,
            'face': False,
            'temp': False
        },
        'library': {
            'library_type': 'aplibrary',
            'library_name': 'Travels',
            'library_path': '/Volumes/LaCie/_MASTER_Aperture_20190520/Travels.aplibrary',
            'is': 'is_master',
            'is_master': True,
            'is_preview': False,
            'is_thumbnail': False,
            'is_proxy': False
        },
        'desired': True
    },
    # /Volumes/Padawan/_Pictures/Aperture Library Collections/_Libraries/iPhoto Library__1.photolibrary
    # Library -photolibrary
    '/Volumes/Padawan/_Pictures/Aperture Library Collections/_Libraries/iPhoto Library__1.photolibrary/Masters/2014/12/20/20141220-165140/IMG_0024.jpg': {
        'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/_Libraries/iPhoto Library__1.photolibrary/Masters/2014/12/20/20141220-165140/IMG_0024.jpg',
        'image_name': {
            'name': 'IMG_0024',
            'path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/_Libraries/iPhoto Library__1.photolibrary/Masters/2014/12/20/20141220-165140/IMG_0024.jpg',
            'extention': '.jpg',
            'thumbnail': False,
            'copy in name': False,
            'copy subfix': False,
            'face': False,
            'temp': False
        },
        'library': {
            'library_type': 'photoslibrary',
            'library_name': 'iPhoto Library__1',
            'library_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/_Libraries/iPhoto Library__1.photolibrary',
            'is': 'is_master',
            'is_master': True,
            'is_preview': False,
            'is_thumbnail': False,
            'is_proxy': False
        },
        'desired': True
    },
    # Undesired -- Previews
    '/Volumes/Padawan/_Pictures/Aperture Library Collections/_Libraries/Aperture Library__1.aplibrary/Previews/2011/01/17/20110117-164607/2CZ5vdr2RwqvD0lwTV6+kw/IMGP7419.jpg': {
        'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/_Libraries/Aperture Library__1.aplibrary/Previews/2011/01/17/20110117-164607/2CZ5vdr2RwqvD0lwTV6+kw/IMGP7419.jpg',
        'image_name': {
            'name': 'IMGP7419',
            'path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/_Libraries/Aperture Library__1.aplibrary/Previews/2011/01/17/20110117-164607/2CZ5vdr2RwqvD0lwTV6+kw/IMGP7419.jpg',
            'extention': '.jpg',
            'thumbnail': False,
            'copy in name': False,
            'copy subfix': False,
            'face': False,
            'temp': False
        },
        'library': {
            'library_type': 'aplibrary',
            'library_name': 'Aperture Library__1',
            'library_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/_Libraries/Aperture Library__1.aplibrary',
            'is': 'is_preview',
            'is_master': False,
            'is_preview': True,
            'is_thumbnail': False,
            'is_proxy': False
        },
        'desired': False
    },
    # Undesired -- Thumbnail - Face
    '/Volumes/Padawan/_Pictures/_Libaries/iPhoto Library #4/Thumbnails/2012/06/05/20120605-235330/_IGP6908_face0.jpg': {
        'file_path': '/Volumes/Padawan/_Pictures/_Libaries/iPhoto Library #4/Thumbnails/2012/06/05/20120605-235330/_IGP6908_face0.jpg',
        'image_name': {
            'name': '_IGP6908_face0',
            'path': '/Volumes/Padawan/_Pictures/_Libaries/iPhoto Library #4/Thumbnails/2012/06/05/20120605-235330/_IGP6908_face0.jpg',
            'extention': '.jpg',
            'thumbnail': False,
            'copy in name': False,
            'copy subfix': False,
            'face': True,
            'temp': False
        },
        'library': {
            'library_type': 'iphoto',
            'library_name': 'iPhoto Library #4',
            'library_path': '/Volumes/Padawan/_Pictures/_Libaries/iPhoto Library #4',
            'is': 'is_thumbnail',
            'is_master': False,
            'is_preview': False,
            'is_thumbnail': True,
            'is_proxy': False
        },
        'desired': False
    },
    # Undesired -- Thumbnail
    '/Volumes/Padawan/_Pictures/_Libaries/iPhoto Library #4/Thumbnails/2012/06/05/20120605-235330/_IGP6918.jpg': {
        'file_path': '/Volumes/Padawan/_Pictures/_Libaries/iPhoto Library #4/Thumbnails/2012/06/05/20120605-235330/_IGP6918.jpg',
        'image_name': {
            'name': '_IGP6918',
            'path': '/Volumes/Padawan/_Pictures/_Libaries/iPhoto Library #4/Thumbnails/2012/06/05/20120605-235330/_IGP6918.jpg',
            'extention': '.jpg',
            'thumbnail': False,
            'copy in name': False,
            'copy subfix': False,
            'face': False,
            'temp': False
        },
        'library': {
            'library_type': 'iphoto',
            'library_name': 'iPhoto Library #4',
            'library_path': '/Volumes/Padawan/_Pictures/_Libaries/iPhoto Library #4',
            'is': 'is_thumbnail',
            'is_master': False,
            'is_preview': False,
            'is_thumbnail': True,
            'is_proxy': False
        },
        'desired': False
    },
    # Undesired -- Preview
    '/Volumes/Padawan/_Pictures/_Libaries/iPhoto Library #2/Previews/2007/Kakadu/IMG_0680.JPG': {
        'file_path': '/Volumes/Padawan/_Pictures/_Libaries/iPhoto Library #2/Previews/2007/Kakadu/IMG_0680.JPG',
        'image_name': {
            'name': 'IMG_0680',
            'path': '/Volumes/Padawan/_Pictures/_Libaries/iPhoto Library #2/Previews/2007/Kakadu/IMG_0680.JPG',
            'extention': '.JPG',
            'thumbnail': False,
            'copy in name': False,
            'copy subfix': False,
            'face': False,
            'temp': False
        },
        'library': {
            'library_type': 'iphoto',
            'library_name': 'iPhoto Library #2',
            'library_path': '/Volumes/Padawan/_Pictures/_Libaries/iPhoto Library #2',
            'is': 'is_preview',
            'is_master': False,
            'is_preview': True,
            'is_thumbnail': False,
            'is_proxy': False
        },
        'desired': False
    },
    '/Volumes/Padawan/_Pictures/_Backups/Apeture_Import_Backups/2014_SouthAmerica /20150119/.__IGP8686.PEF': {
        'file_path': '/Volumes/Padawan/_Pictures/_Backups/Apeture_Import_Backups/2014_SouthAmerica /20150119/.__IGP8686.PEF',
        'image_name': {
            'name': '.__IGP8686',
            'path': '/Volumes/Padawan/_Pictures/_Backups/Apeture_Import_Backups/2014_SouthAmerica /20150119/.__IGP8686.PEF',
            'extention': '.PEF',
            'thumbnail': False,
            'copy in name': False,
            'copy subfix': False,
            'face': False,
            'temp': True
        },
        'library': {
            'library_type': '',
            'library_name': '',
            'library_path': '',
            'is': '',
            'is_master': False,
            'is_preview': False,
            'is_thumbnail': False,
            'is_proxy': False
        },
        'desired': False
    },
    '/Volumes/Padawan/_Pictures/_Backups/Apeture_Import_Backups/2014_SouthAmerica /20150214/._IMGP0110.JPG': {
        'file_path': '/Volumes/Padawan/_Pictures/_Backups/Apeture_Import_Backups/2014_SouthAmerica /20150214/._IMGP0110.JPG',
        'image_name': {
            'name': '._IMGP0110',
            'path': '/Volumes/Padawan/_Pictures/_Backups/Apeture_Import_Backups/2014_SouthAmerica /20150214/._IMGP0110.JPG',
            'extention': '.JPG',
            'thumbnail': False,
            'copy in name': False,
            'copy subfix': False,
            'face': False,
            'temp': True
        },
        'library': {
            'library_type': '',
            'library_name': '',
            'library_path': '',
            'is': '',
            'is_master': False,
            'is_preview': False,
            'is_thumbnail': False,
            'is_proxy': False
        },
        'desired': False
    },
    # # Undesired -- Preview
    '/Volumes/LaCie/_MASTER_Aperture_20190520/Travels.aplibrary/Masters/2012/06/16/20120616-232546/396563_10150505685524265_927455613_n.jpg': {
        'file_path': '/Volumes/LaCie/_MASTER_Aperture_20190520/Travels.aplibrary/Masters/2012/06/16/20120616-232546/396563_10150505685524265_927455613_n.jpg',
        'image_name': {
            'name': '396563_10150505685524265_927455613_n',
            'path': '/Volumes/LaCie/_MASTER_Aperture_20190520/Travels.aplibrary/Masters/2012/06/16/20120616-232546/396563_10150505685524265_927455613_n.jpg',
            'extention': '.jpg',
            'thumbnail': False,
            'copy in name': False,
            'copy subfix': False,
            'face': False,
            'temp': True
        },
        'library': {
            'library_type': 'aplibrary',
            'library_name': 'Travels',
            'library_path': '/Volumes/LaCie/_MASTER_Aperture_20190520/Travels.aplibrary',
            'is': 'is_master',
            'is_master': True,
            'is_preview': False,
            'is_thumbnail': False,
            'is_proxy': False
        },
        'desired': False
    },

    # # TEMPLATE
    # '': {
    #     'file_path': '',
    #     'image_name': {
    #         'name': '',
    #         'path': '',
    #         'extention': '',
    #         'thumbnail': False,
    #         'copy in name': False,
    #         'copy subfix': False,
    #         'face': False,
    #         'temp': False
    #     },
    #     'library': {
    #         'library_type': '',
    #         'library_name': '',
    #         'library_path': '',
    #         'is': '',
    #         'is_master': False,
    #         'is_preview': False,
    #         'is_thumbnail': False,
    #         'is_proxy': False
    #     },
    #     'desired': False
    # },
}


# file_paths = {
#     path : details
#     for path, details in files.items()
# }


@pytest.fixture()
def file_path(request):
    return request


@pytest.mark.parametrize("test_file_path, expected_image", [
    (path, file['image_name'])
    for path, file in files.items()
])
def test__clean_name(test_file_path, expected_image):
    assert clean_name(test_file_path) == expected_image


@pytest.mark.parametrize("test_file_path, expected_library", [
    (path, file['library'])
    for path, file in files.items()
])
def test_extract_library(test_file_path, expected_library):
    assert extract_library(test_file_path) == expected_library


@pytest.mark.parametrize("test_file_path, expected_desired", [
    (path, file['desired'])
    for path, file in files.items()
])
def test_is_desired(test_file_path, expected_desired):
    file = files[test_file_path]['image_name']
    library = files[test_file_path]['library']
    assert is_desired(file, library) == expected_desired
