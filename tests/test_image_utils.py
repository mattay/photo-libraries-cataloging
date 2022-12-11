import pytest
from photologue.images_utils import original_date


@pytest.mark.parametrize("test__original_date, expected_dates", [
    ("2012:12:25 08:39:41", "2012:12:25"),
    ("2012:01:15 17:23:38+10:00", "2012:01:15"),
    ("    :  :     :  :", '    :  :  '),
    ("", '    :  :  '),
])
def test__original_date(test__original_date, expected_dates):
    assert original_date(test__original_date) == expected_dates
