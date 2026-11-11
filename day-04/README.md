# Day 04 – Safe Folder Organizer
Part of my #30DaysOfAutomation challenge.

## The problem
Everyone has a messy Downloads folder: hundreds of files, no order, and no idea where anything is. Sorting it by hand takes an hour. But a tool that moves your files can also make a mess: one wrong path and it organizes the wrong folder, and there's no way back.

## What I built
A command-line tool that sorts the files of a folder into category folders (Images, Documents, Videos, ...) and can **undo the last run**.

The tool is built around safety: it checks the path first, shows a plan before touching anything, never overwrites a file, and keeps a record of every run so it can be undone.

## How it works
1. **Validate** the folder. Empty paths, missing folders, drive roots, the home folder and system folders are refused.
2. **Plan** where every file goes, without moving anything.
3. **Show** the plan and ask for confirmation (`--dry-run` stops here and writes nothing).
4. **Move** the files, logging each move.
5. **Save a session file** (JSON) with every move, so the run can be undone.

### Functions
| Function | What it does |
|----------|--------------|
| `validate_folder()` | Refuses unsafe paths before anything is created |
| `plan_moves()` | Decides the destination of every file, moves nothing |
| `unique_path()` | Adds ` (1)`, ` (2)` to a name instead of overwriting a file |
| `organize()` | Shows the plan, asks for confirmation, moves the files |
| `save_session()` | Writes one JSON file per run (the memory used by rollback) |
| `rollback()` | Restores the files of the last run that was not undone yet |

### Safety rules
- `--dry-run` shows what would happen and writes nothing to disk
- A file is never overwritten
- Hidden files, temporary downloads (`.crdownload`, `.part`) and the script itself are skipped
- Only files directly inside the folder are touched, never subfolders
- Rollback skips a file if its original path is already occupied, instead of overwriting it
- A session file is saved even if the run is interrupted, so rollback still works

## How to run
```bash
python folder_organizer.py "path/to/folder" --dry-run     # preview only
python folder_organizer.py "path/to/folder"               # organize (asks first)
python folder_organizer.py "path/to/folder" --rollback    # undo the last run
```

| Option | What it does |
|--------|--------------|
| `--dry-run` | Show the plan, change nothing |
| `--rollback` | Undo the last run |
| `--yes` | Skip the confirmation question |

If no folder is given, the tool asks for one.

## Output
Preview:
```
Plan for /home/user/test:
  Audio: 1 file(s)
  Documents: 2 file(s)
  Images: 1 file(s)
  Other: 1 file(s)
  skipped: .hidden (hidden file)
  skipped: e.crdownload (temporary download)

Dry run: nothing was moved and nothing was written.
```

Organize:
```
START session=c1d38c0d... folder=/home/user/test
MOVED Song.MP3 -> Audio
MOVED a.jpg -> Images
MOVED b.pdf -> Documents
MOVED c.txt -> Documents
MOVED d.xyz -> Other
SKIPPED .hidden (hidden file)
SKIPPED e.crdownload (temporary download)
DONE moved=5 skipped=2 failed=0
```

Rollback:
```
Last run: 2026-11-11T19:40:34 (5 file(s) moved)
ROLLBACK START session=c1d38c0d...
RESTORED d.xyz
RESTORED c.txt
RESTORED b.pdf
RESTORED a.jpg
RESTORED Song.MP3
ROLLBACK DONE restored=5 skipped=0 failed=0
```

Unsafe input is refused:
```
Error: No folder given. Refusing to guess which folder you meant.
Error: Refusing to organize a drive root or your home folder: /
```

## What I learned
- `argparse` to build a real command-line interface with options
- `pathlib`: `resolve()`, `parents`, `rmdir()` and `iterdir()`
- Planning before acting: separating "decide" from "do" makes dry-run and confirmation almost free
- Using a JSON file as the memory of a tool, instead of reading a text log
- `try/finally` to save the record even when a run is interrupted
- Checking user input before any side effect happens

**A lesson from testing:** my first version looked fine, but when I actually ran it I found three real bugs:
1. Rollback never worked. It read the text log and the session id was parsed with extra characters, so it always said there was nothing to undo.
2. The "folder not found" check was dead code, because the logs folder was created first, which created the missing folder too.
3. Pressing Enter on an empty path organized whatever folder the terminal was in.

Reading the code is not enough. A tool that moves files needs to be tested on purpose: wrong paths, empty input, name clashes, two runs in a row, and undo.

## Limitations and next steps
- Only files directly inside the folder are organized, not subfolders.
- Categories are fixed in the code. A settings file would make them editable.
- Rollback works only for runs made by this version (older runs have no session file).
- Next: schedule it to run automatically, so Downloads stays organized by itself.

## Resources I used
- [argparse – Python docs](https://docs.python.org/3/library/argparse.html)
- [pathlib – Python docs](https://docs.python.org/3/library/pathlib.html)
- [shutil – Python docs](https://docs.python.org/3/library/shutil.html)
- [json – Python docs](https://docs.python.org/3/library/json.html)
- [logging – Python docs](https://docs.python.org/3/library/logging.html)