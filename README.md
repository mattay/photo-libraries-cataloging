# photo-libraries-cataloging

## Setup

Install required tool and python libraries.

Using Homebrew we'll install:

- [exiftool](https://exiftool.org) - Image metadata extraction (Perl)
- [sqlite](https://www.sqlite.org) Local file based SQL database
- [pcre](https://www.pcre.org) regex for sqlite
- [poetry](https://python-poetry.org) Python packaging and dependency management
- [yq](https://github.com/mikefarah/yq) Process YAML, JSON, XML, CSV and properties documents from the CLI (Go)

```bash
brew install ExifTool sqlite pcre poetry yq
```

### SQLite configuration

#### Enable Support for regex

```bash
git clone https://github.com/ralight/sqlite3-pcre.git
cd sqlite3-pcre
cc -shared -o sqlite3-pcre.so -I/usr/local/opt/pcre/include -fPIC -W -Werror pcre.c -L/usr/local/opt/pcre/lib -lpcre -lsqlite3
echo ".load '`pwd`/sqlite3-pcre.so'" >> ~/.sqliterc
```

References

- [https://stackoverflow.com/questions/5071601/how-do-i-use-regex-in-a-sqlite-query]
- [https://gist.github.com/janfri/a3e61731864a63554ba6f32bdc7179aa]

May need to setup Apple's Developer CommandLineTools

```bash
xcode-select --install
```

#### Enable Support foreign key constrats

Run the following `SQL` statement in SQLite to enable foreign keys needed to optimize data fetching.

```sql
PRAGMA foreign_keys = ON;
```

### Python setup

```bash
poetry install
```

## Running

### Configure

Rules are configured in `./config.xml`

```yml
import:
    volumes:
        # <volume name>:
            # - Volume paths to include in searches
        Jedi:
            - /Volumes/Jedi/ApertureLibraryBackups
            - /Volumes/Jedi/Photos
    extentions:
        # - file extentions in include in searches
        - .PEF
        - .DNG
        - .RW2
        - .jpg
        - .JPG
        - .jpeg
    ignore:
        # - partial regex match in a file path to ignore
        - /Previews/
        - _n.jpg
        - _o.jpg
        - \.__IGP
        - '[T|t]humb'

raw_extentions:
  - .PEF
  - .DNG
  - .RW2

cleanup:
  preferred:
    # images in these paths (or file) are preferenced when picking a master to keep
    paths:
        - path
    files:
        - filepath

  ignore:
    # images in these paths (or file) we don't care to keep.
    paths:
        - path
    files:
        - filepath

  camera_rules:
    # list of camera models
    <camera model>:
      # Optional Note Properties
      Owner: owner name
      Location: Church
      Content: Wedding
      Action Steps: Check Dropbox for duplicates
      Plan:
      Notes: Ignore exports
      # Filtering conditions
      filters:
        # Ordered list of perfered conditions to match on
        # options -> extentions | checksums
        - condition: extentions
        # if extention, list the set of extentions
        - matches: !!set {.JPG, .jpg}
        # Action to take for matching the condition.
        # options -> keep | ignore
        - action: keep
        # list of optional file properties to match on
        file_props:
          file_extention: .JPG
          quality: Best
          software: Ver 1.00
          modified: 0
          has_copy_in_subfix: 0
          mod_date:

```

### Processing

Commands

<!-- - **cleanup** -  -->
- **clearlogs** - Delete all log files.
- **collect** Find image files and colllect stas and exif.
- **process** - Proccess collected images to discover masters, copies, filtered and ignored.
- **clearlogs** Deletes all log files.
- **summary** Stats on file patterns in collection.

```bash
./run.sh <command>
```

## Developmnet

Commands

- **lint** Lint code.
- **test** Unit tests.
- **profile** Profile code.

Lint code

```bash
./run.sh lint
```

Run unit tests

```bash
./run.sh test
```

Profile code, Check run.sh to see which command is being profiled

```bash
./run.sh profile
```

## Notes

Might need to remove

- file_path like "%/n%.jpg"
- file_path like "%_n.jpg"
- file_path like "%_o.jpg"
- file_path like "%.__IGP%.PEF"
- file_path like "/Volumes/Padawan/_Pictures/Aperture Library Collections/_Libraries/iPhoto Library copy/Thumbnails/%"
- like "IMG_%.JPG" -- iPhone

These files have need to be manually dealt with

``` bash
/Users/matthew/Dropbox/Camera Uploads/2013-08-27 19.43.05.jpg: stat: File name too long
```

```bash
stat: The man un-tying the boat is the man in the next photo.jpg: stat: No such file or directory
```

```bash
stat: The man un-tying the boat is the man in the next photo_1024.jpg: stat: No such file or directory
```

```bash
2022-12-13
/Users/matthew/Dropbox/Camera Uploads/2013-08-27 19.43.05.jpg:
```
