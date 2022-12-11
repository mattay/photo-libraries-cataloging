from typing import Any, Optional
# from pprint import pprint
import logging
import sqlite3


class Catalogue:
    """
        Catalogue is the interface to the SQLite Database
    """

    def __init__(self, indexing_cabinate):
        self.logger = logging.getLogger('Catalogue')
        self.conn = sqlite3.connect(indexing_cabinate)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

        """
            Setup Database Tables
        """
        # RESET = True
        # if RESET:
        #   self.logger.warn('Resetting Database Tables!')
        #   self.cur.execute('''--sql DROP TABLE IF EXISTS file;''')
        #   self.cur.execute('''--sql DROP TABLE IF EXISTS library;''')
        #   self.cur.execute('''--sql DROP TABLE IF EXISTS exif;''')
        #   self.cur.execute('''--sql DROP TABLE IF EXISTS realationships;''')

        """ File paths """
        self.cur.execute('''--sql
            CREATE TABLE IF NOT EXISTS file
            (
                file_path text PRIMARY KEY,
                file_name text,
                file_extention text,
                checksum text,
                size int,
                focus_on int DEFAULT 0,
                is_raw_image int DEFAULT 0,
                has_copy_in_name int DEFAULT 0,
                has_copy_in_subfix int DEFAULT 0
            );
        ''')
        #  indexes
        self.cur.execute('''--sql
            CREATE INDEX IF NOT EXISTS
                idx_file_filename ON FILE (file_name) ;
        ''')
        self.cur.execute('''--sql
            CREATE INDEX IF NOT EXISTS
                idx_file_checksum ON FILE (checksum);
        ''')

        """ Library """
        self.cur.execute('''--sql
            CREATE TABLE IF NOT EXISTS library
            (
                file_path text PRIMARY KEY,
                library_path text,
                library_name text,
                library_type text,
                --is_master int DEFAULT 0,
                --is_preview int DEFAULT 0,
                --is_thumbnail int DEFAULT 0,
                --is_proxy int DEFAULT 0,
                FOREIGN KEY(file_path) REFERENCES file(file_path) ON DELETE CASCADE
            );
        ''')
        #  indexes
        self.cur.execute('''--sql
            CREATE INDEX IF NOT EXISTS
                idx_library_path ON library (library_path);
        ''')

        """ exif """
        self.cur.execute('''--sql
            CREATE TABLE IF NOT EXISTS exif
                (
                    file_path text PRIMARY KEY,
                    date_time_original text,
                    date_time_modifed text,
                    camera_make text,
                    camera_model text,
                    quality text,
                    x_resolution int,
                    y_resolution int,
                    image_height int,
                    image_width int,
                    resolution_unit text,
                    software text,
                    color_space text,
                    FOREIGN KEY(file_path) REFERENCES file(file_path) ON DELETE CASCADE
                );
        ''')
        #  indexes
        self.cur.execute('''--sql
            CREATE INDEX IF NOT EXISTS
                idx_exif_camera ON exif (camera_model);
        ''')

        """ Realationships """
        self.cur.execute('''--sql
            CREATE TABLE IF NOT EXISTS realationships
            (
                file_path text NOT NULL,
                is_a text NOT NULL,
                of_file_path text DEFAULT EMPTY,
                FOREIGN KEY(file_path) REFERENCES file(file_path) ON DELETE CASCADE,
                FOREIGN KEY(of_file_path) REFERENCES file(file_path) ON DELETE CASCADE,
                UNIQUE(file_path, is_a, of_file_path)
            );
        ''')

        # Clean up dirty Data before use
        self.__clean_up()

    def __del__(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    #
    # Internal query utils
    #

    def __clean_up(self) -> None:
        # Clean extention for file_name
        query = """--sql
            UPDATE file
            SET file_name = replace(file_name, '.JPG', '')
            WHERE file_name LIKE '%.JPG'
            ;
        """
        self.cur.execute(query)
        self.save()

    def __add(self, query: str, data) -> None:
        # TODO:
        try:
            with self.conn:
                self.cur.execute(query, data)
                # self.cur.execute('COMMIT')

        except sqlite3.Warning as w:
            self.logger.warn("Warning occurred: ", w)
            self.logger.warn("Query: ", query)

        except sqlite3.Error as e:
            self.logger.error("Error occurred: ", e)
            self.logger.error("Query: ", query)
            exit(1)

    def __request_list(self, query: str, args: Optional[Any] = None) -> list[str]:
        try:
            if args:
                self.cur.execute(query, args)
            else:
                self.cur.execute(query)
                return [x[0] for x in self.cur.fetchall()]

        except sqlite3.Warning as w:
            self.logger.warn("Warning occurred: ", w)
            self.logger.warn("Query: ", query)

        except sqlite3.Error as e:
            self.logger.error("Error occurred: ", e)
            self.logger.error("Query: ", query)
            exit(1)
        return []

    def __request_results(self, query: str, args: Optional[Any] = None) -> list[dict]:
        try:
            if args:
                self.cur.execute(query, args)
            else:
                self.cur.execute(query)
            return [dict(row) for row in self.cur.fetchall()]

        except sqlite3.Warning as w:
            self.logger.warn("Warning occurred: ", w)
            self.logger.warn("Query: ", query)

        except sqlite3.Error as e:
            self.logger.error("Error occurred: ", e)
            self.logger.error("Query: ", query)
            exit(1)
        return []

    #
    # Add Records
    #

    def add_file(self, image: dict) -> None:
        query = """--sql
            INSERT OR IGNORE INTO file
            (
                file_path,
                file_name,
                file_extention,
                is_raw_image,
                has_copy_in_name,
                has_copy_in_subfix
            )
            VALUES (?, ?, ?, ?, ?, ?);
        """
        data = (
            image['path'],
            image["name"],
            image["extention"],
            image['raw_image'],
            image["copy in name"],
            image["copy subfix"]
        )

        self.__add(query, data)

    def add_checksum(self, file_path: str, checksum) -> None:
        query = """--sql
            UPDATE file
            SET checksum=:checksum
            WHERE file_path=:file_path;
        """
        data = {
            "checksum": checksum,
            "file_path": file_path
        }

        self.__add(query, data)

    def add_filestats(self, file_path: str, filestats) -> None:
        query = """--sql
            UPDATE file
            SET
                    size=:size
            WHERE file_path=:file_path;
        """
        data = {
            'size': filestats["size"],
            "file_path": file_path
        }

        self.__add(query, data)

    def add_library(self, file_path: str, library) -> None:
        query = """--sql
            INSERT OR IGNORE INTO library
            (
                file_path,
                library_path,
                library_name,
                library_type
            )
            VALUES (?, ?, ?, ?);
        """
        data = (
            file_path,
            library["library_path"],
            library["library_name"],
            library["library_type"]
        )
        self.__add(query, data)

    def add_exif(self, file_path: str, exif) -> None:
        query = """--sql
                INSERT OR IGNORE INTO exif
                (
                    file_path,
                    date_time_original ,
                    date_time_modifed ,
                    camera_make ,
                    camera_model ,
                    quality ,
                    x_resolution ,
                  y_resolution ,
                    image_height ,
                    image_width ,
                    resolution_unit,
                    software,
                    color_space
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """
        data = (
            file_path,
            exif["date_time_original"],
            exif["date_time_modifed"],
            exif["camera_make"],
            exif["camera_model"],
            exif["quality"],
            exif["x_resolution"],
            exif["y_resolution"],
            exif["image_height"],
            exif["image_width"],
            exif["resolution_unit"],
            exif["software"],
            exif["color_space"]
        )
        self.__add(query, data)

    def save(self) -> None:
        try:
            self.cur.execute('COMMIT')

        except sqlite3.Warning as w:
            self.logger.warn("Warning occurred: ", w)
            self.logger.warn("Query: ", 'COMMIT')

        except sqlite3.Error as e:
            self.logger.error("Error occurred: ", e)
            self.logger.error("Query: ", 'COMMIT')
            exit(1)

    def add_relationship(self, file_path: str, is_a: str, of_file_path: str) -> None:
        query = """--sql
            INSERT OR IGNORE INTO realationships
            (
                file_path, is_a, of_file_path
            )
            VALUES (?, ?, ?);
        """
        data = (
            file_path, is_a, of_file_path
        )
        self.__add(query, data)

    #
    # Requests
    #

    def images(self) -> list[str]:
        query = """--sql
            SELECT DISTINCT f.file_name
            FROM file f
            ORDER BY file_name;
            """
        return self.__request_list(query)

    def image_paths(self, image) -> list[str]:
        query = """--sql
            SELECT file_path
            FROM file
            WHERE file_name=:file_name;
        """
        return self.__request_list(query, {"file_name": image})

    def image_files(self, image: str) -> list[dict]:
        query = """--sql
            SELECT *
            FROM file f
            LEFT JOIN "library" l ON f.file_path = l.file_path
            WHERE f.file_name = ?
        ;"""
        return self.__request_results(query, (image,))

    def files(self, missing: str = "") -> list[str]:
        query = """--sql
            SELECT f.file_path
            FROM "file" f
            ;
        """
        if missing == "exifs":
            query = """--sql
                SELECT f.file_path
                FROM "file" f
                WHERE f.file_path NOT IN (
                    SELECT e.file_path FROM exif e
                );
            """
        elif missing == "stats":
            query = """--sql
                SELECT f.file_path
                FROM "file" f
                WHERE f.size IS NULL
                ;
            """
        elif missing == "checksums":
            query = """--sql
                SELECT f.file_path
                FROM "file" f
                WHERE f.checksum IS NULL
                ;
            """

        return self.__request_list(query)

    def cameras(self) -> list[str]:
        query = """--sql
            SELECT distinct e.camera_model
            FROM exif e
            ;
        """
        return self.__request_list(query)

    def camera_files(self, camera: str) -> list[dict]:
        query = """--sql
            SELECT
                e.camera_model,
                e.date_time_original,
                f.file_name,
                f.checksum,
                f.size,
                f.file_extention,
                f.has_copy_in_subfix,
                f.file_path,
                e.quality,
                e.software,
                e.color_space,
                e.date_time_modifed,
                l.library_type,
                l.library_name,
                l.library_path
            FROM
                "file" f
                JOIN exif e ON e.file_path = f.file_path and e.camera_model = ?
                LEFT JOIN "library" l on l.file_path = f.file_path
        ;"""
        return self.__request_results(query, (camera,))
