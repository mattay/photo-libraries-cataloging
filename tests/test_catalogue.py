import pytest
from photologue.catalogue import Catalogue


@pytest.fixture
def catalogue():
    c = Catalogue(':memory:')
    yield c
    c.conn.close()


@pytest.fixture
def cursor(catalogue):
    return catalogue.conn.cursor()


def test_all_tables_created(cursor):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = {row[0] for row in cursor.fetchall()}
    assert tables == {
        'exif', 'file', 'library', 'realationships'
    }


# -- file table --

FILE_COLUMNS = {
    'file_path': 'text',
    'file_name': 'text',
    'file_extention': 'text',
    'checksum': 'text',
    'size': 'int',
    'focus_on': 'int',
    'is_raw_image': 'int',
    'has_copy_in_name': 'int',
    'has_copy_in_subfix': 'int',
}


def test_file_columns(cursor):
    cursor.execute("PRAGMA table_info(file)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    for col, expected_type in FILE_COLUMNS.items():
        assert col in columns, f"Missing column: file.{col}"
        actual = columns[col].lower()
        assert actual == expected_type.lower(), (
            f"Wrong type for file.{col}: "
            f"{columns[col]} != {expected_type}"
        )


def test_file_primary_key(cursor):
    cursor.execute("PRAGMA table_info(file)")
    for row in cursor.fetchall():
        if row[1] == 'file_path':
            assert row[5] == 1, "file.file_path should be PRIMARY KEY"
            return
    pytest.fail("file.file_path column not found")


def test_file_indexes(cursor):
    cursor.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='index' AND tbl_name='file'"
    )
    indexes = {row[0] for row in cursor.fetchall()}
    assert 'idx_file_filename' in indexes
    assert 'idx_file_checksum' in indexes


# -- library table --

LIBRARY_COLUMNS = {
    'file_path': 'text',
    'library_path': 'text',
    'library_name': 'text',
    'library_type': 'text',
}


def test_library_columns(cursor):
    cursor.execute("PRAGMA table_info(library)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    for col, expected_type in LIBRARY_COLUMNS.items():
        assert col in columns, f"Missing column: library.{col}"
        actual = columns[col].lower()
        assert actual == expected_type.lower(), (
            f"Wrong type for library.{col}: "
            f"{columns[col]} != {expected_type}"
        )


def test_library_primary_key(cursor):
    cursor.execute("PRAGMA table_info(library)")
    for row in cursor.fetchall():
        if row[1] == 'file_path':
            assert row[5] == 1, (
                "library.file_path should be PRIMARY KEY"
            )
            return
    pytest.fail("library.file_path column not found")


def test_library_foreign_key(cursor):
    cursor.execute("PRAGMA foreign_key_list(library)")
    fks = [(row[2], row[3]) for row in cursor.fetchall()]
    assert ('file', 'file_path') in fks


def test_library_indexes(cursor):
    cursor.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='index' AND tbl_name='library'"
    )
    indexes = {row[0] for row in cursor.fetchall()}
    assert 'idx_library_path' in indexes


# -- exif table --

EXIF_COLUMNS = {
    'file_path': 'text',
    'date_time_original': 'text',
    'date_time_modifed': 'text',
    'camera_make': 'text',
    'camera_model': 'text',
    'quality': 'text',
    'x_resolution': 'int',
    'y_resolution': 'int',
    'image_height': 'int',
    'image_width': 'int',
    'resolution_unit': 'text',
    'software': 'text',
    'color_space': 'text',
}


def test_exif_columns(cursor):
    cursor.execute("PRAGMA table_info(exif)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    for col, expected_type in EXIF_COLUMNS.items():
        assert col in columns, f"Missing column: exif.{col}"
        actual = columns[col].lower()
        assert actual == expected_type.lower(), (
            f"Wrong type for exif.{col}: "
            f"{columns[col]} != {expected_type}"
        )


def test_exif_primary_key(cursor):
    cursor.execute("PRAGMA table_info(exif)")
    for row in cursor.fetchall():
        if row[1] == 'file_path':
            assert row[5] == 1, "exif.file_path should be PRIMARY KEY"
            return
    pytest.fail("exif.file_path column not found")


def test_exif_foreign_key(cursor):
    cursor.execute("PRAGMA foreign_key_list(exif)")
    fks = [(row[2], row[3]) for row in cursor.fetchall()]
    assert ('file', 'file_path') in fks


def test_exif_indexes(cursor):
    cursor.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='index' AND tbl_name='exif'"
    )
    indexes = {row[0] for row in cursor.fetchall()}
    assert 'idx_exif_camera' in indexes


# -- realationships table --

RELATIONSHIPS_COLUMNS = {
    'file_path': 'text',
    'is_a': 'text',
    'of_file_path': 'text',
}


def test_relationships_columns(cursor):
    cursor.execute("PRAGMA table_info(realationships)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    for col, expected_type in RELATIONSHIPS_COLUMNS.items():
        assert col in columns, (
            f"Missing column: realationships.{col}"
        )
        actual = columns[col].lower()
        assert actual == expected_type.lower(), (
            f"Wrong type for realationships.{col}: "
            f"{columns[col]} != {expected_type}"
        )


def test_relationships_foreign_keys(cursor):
    cursor.execute("PRAGMA foreign_key_list(realationships)")
    fks = {(row[2], row[3]) for row in cursor.fetchall()}
    assert ('file', 'file_path') in fks
    assert ('file', 'of_file_path') in fks


def test_relationships_unique_constraint(cursor):
    cursor.execute(
        "SELECT sql FROM sqlite_master "
        "WHERE type='table' AND name='realationships'"
    )
    create_sql = cursor.fetchone()[0]
    assert 'UNIQUE' in create_sql


def test_relationships_indexes(cursor):
    cursor.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='index' AND tbl_name='realationships'"
    )
    indexes = {row[0] for row in cursor.fetchall()}
    assert 'idx_realationships_is_a' in indexes
