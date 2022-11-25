# photo-libraries-cataloging

## Setup
Install required tool and python libraries.

Using Homebrew we'll install:
- exiftool (Image metadata extraction)
- sqlite

```bash
./setup.sh
```

### Enabling Foreign Key Support
Run the following SQL statement in SQLite to enable foreign keys needed to optimize data fetching.
```sql
PRAGMA foreign_keys = ON;
```
