import pytest
from photologue.clean.clean_group import (
    group_by_raw_plus_checksums,
    group_by_paths
)

DMC_LX3_P1000847 = [
    {'checksum': 1487073708, 'file_extention': '.JPG', 'file_path': '/Volumes/LaCie/_MASTER_Aperture_20190520/ForSale.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.JPG'},
    {'checksum': 1414083411, 'file_extention': '.RW2', 'file_path': '/Volumes/LaCie/_MASTER_Aperture_20190520/ForSale.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.RW2'},
    {'checksum': 1487073708, 'file_extention': '.JPG', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__1.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.JPG'},
    {'checksum': 1414083411, 'file_extention': '.RW2', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__1.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.RW2'},
    {'checksum': 1487073708, 'file_extention': '.JPG', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__2.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.JPG'},
    {'checksum': 1414083411, 'file_extention': '.RW2', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__2.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.RW2'},
    {'checksum': 1487073708, 'file_extention': '.JPG', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__3.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.JPG'},
    {'checksum': 1414083411, 'file_extention': '.RW2', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__3.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.RW2'},
    {'checksum': 1487073708, 'file_extention': '.JPG', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ItemsForSale__4.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.JPG'},
    {'checksum': 1414083411, 'file_extention': '.RW2', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ItemsForSale__4.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.RW2'},
]

DMC_LX3_P1000847_group_by_paths = {
    '/Volumes/LaCie/_MASTER_Aperture_20190520/ForSale.aplibrary/Masters/2010/02/28/20100228-211134': {
        '.JPG': {'checksum': 1487073708, 'file_extention': '.JPG', 'file_path': '/Volumes/LaCie/_MASTER_Aperture_20190520/ForSale.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.JPG'},
        '.RW2': {'checksum': 1414083411, 'file_extention': '.RW2', 'file_path': '/Volumes/LaCie/_MASTER_Aperture_20190520/ForSale.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.RW2'}
    },
    '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__1.aplibrary/Masters/2010/02/28/20100228-211134': {
        '.JPG': {'checksum': 1487073708, 'file_extention': '.JPG', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__1.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.JPG'},
        '.RW2': {'checksum': 1414083411, 'file_extention': '.RW2', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__1.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.RW2'}
    },
    '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__2.aplibrary/Masters/2010/02/28/20100228-211134': {
        '.JPG': {'checksum': 1487073708, 'file_extention': '.JPG', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__2.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.JPG'},
        '.RW2': {'checksum': 1414083411, 'file_extention': '.RW2', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__2.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.RW2'}
    },
    '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__3.aplibrary/Masters/2010/02/28/20100228-211134': {
        '.JPG': {'checksum': 1487073708, 'file_extention': '.JPG', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__3.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.JPG'},
        '.RW2': {'checksum': 1414083411, 'file_extention': '.RW2', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__3.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.RW2'}
    },
    '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ItemsForSale__4.aplibrary/Masters/2010/02/28/20100228-211134': {
        '.JPG': {'checksum': 1487073708, 'file_extention': '.JPG', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ItemsForSale__4.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.JPG'},
        '.RW2': {'checksum': 1414083411, 'file_extention': '.RW2', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ItemsForSale__4.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.RW2'}
    }
}

DMC_LX3_P1000847_raw_plus_checksum = {
    'raw': {1414083411: [
        {'checksum': 1414083411, 'file_extention': '.RW2', 'file_path': '/Volumes/LaCie/_MASTER_Aperture_20190520/ForSale.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.RW2'},
        {'checksum': 1414083411, 'file_extention': '.RW2', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__1.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.RW2'},
        {'checksum': 1414083411, 'file_extention': '.RW2', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__2.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.RW2'},
        {'checksum': 1414083411, 'file_extention': '.RW2', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__3.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.RW2'},
        {'checksum': 1414083411, 'file_extention': '.RW2', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ItemsForSale__4.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.RW2'}
    ]},
    'jpg': {1487073708: [
        {'checksum': 1487073708, 'file_extention': '.JPG', 'file_path': '/Volumes/LaCie/_MASTER_Aperture_20190520/ForSale.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.JPG'},
        {'checksum': 1487073708, 'file_extention': '.JPG', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__1.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.JPG'},
        {'checksum': 1487073708, 'file_extention': '.JPG', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__2.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.JPG'},
        {'checksum': 1487073708, 'file_extention': '.JPG', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ForSale__3.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.JPG'},
        {'checksum': 1487073708, 'file_extention': '.JPG', 'file_path': '/Volumes/Padawan/_Pictures/Aperture Library Collections/For Sale/ItemsForSale__4.aplibrary/Masters/2010/02/28/20100228-211134/P1000847.JPG'}
    ]}
}

@pytest.mark.parametrize("test__group_by_paths, expected_pairs", [
    (DMC_LX3_P1000847, DMC_LX3_P1000847_group_by_paths)
])
def test__group_by_paths(test__group_by_paths, expected_pairs):
    assert group_by_paths(test__group_by_paths) == expected_pairs

@pytest.mark.parametrize("test__raw_plus_checksum, expected_pairs", [
    ({}, ({
        'raw': {},
        'jpg': {}
    })),
    (DMC_LX3_P1000847_group_by_paths, DMC_LX3_P1000847_raw_plus_checksum)
])
def test__group_by_raw_plus_checksums(test__raw_plus_checksum, expected_pairs):
    assert group_by_raw_plus_checksums(test__raw_plus_checksum) == expected_pairs
