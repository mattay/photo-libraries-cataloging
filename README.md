# photo-libraries-cataloging

## Setup
Install required tool and python libraries.

Using Homebrew we'll install:
- exiftool (Image metadata extraction)
- sqlite

```bash
brew install ExifTool sqlite pipenv
```

### Enabling Foreign Key Support
Run the following SQL statement in SQLite to enable foreign keys needed to optimize data fetching.
```sql
PRAGMA foreign_keys = ON;
```

### Python setup
```bash
pipenv install -e .
pipenv install -r requirements_dev.txt
```

## Running 
```bash
./run
```

## Notes
Might need to remove
- file_path like "%/n%.jpg"
- file_path like "%_n.jpg"
- file_path like "%_o.jpg"
- file_path like "%.__IGP%.PEF"
- file_path like "/Volumes/Padawan/_Pictures/Aperture Library Collections/_Libraries/iPhoto Library copy/Thumbnails/%"
- like "IMG_%.JPG" -- iPhone