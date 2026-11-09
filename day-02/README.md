# Day 02 – Incremental Backup Tool
Part of my #30DaysOfAutomation challenge.

## The problem
Backing up by copy-paste has three problems:
1. It copies everything every time, even if one file changed.
2. A new copy overwrites the old one, so a bad edit can destroy the only good version.
3. There is no record of what changed between backups.

## What I built
A command-line tool that backs up a folder **incrementally**: it copies only new and modified files, keeps old versions in an archive, and reports what happened.

## How it works
The tool keeps a memory between runs in `manifest.json` (size and modified time of every file at the last backup). Each run:

1. **Scan** the source folder.
2. **Compare** it with the manifest and sort every file into `new`, `modified`, `unchanged` or `deleted`.
3. **Verify** modified files with a SHA-256 hash. If only the timestamp changed but the content is identical, the file is skipped.
4. **Archive** the old version of a modified file to `_archive/<timestamp>/`.
5. **Copy** new and modified files, keeping folder structure and timestamps.
6. **Update** the manifest and print a summary.

Why the hash check is the last step: hashing reads the whole file, which is slow. Size and time are cheap, so they decide first, and the hash only confirms the suspects.

## Safety rules
- Old versions are archived, never overwritten.
- Files deleted from the source are reported but kept in the backup.
- If the process stops halfway, the manifest is not updated, so the next run retries what failed.

## What I learned
- `pathlib`: `rglob`, `relative_to`, `stat`, and building paths with `/`
- `hashlib` with chunked reading, so large files don't fill the memory
- `shutil.copy2` and `shutil.move`
- Using a JSON file as the "memory" of a tool between runs
- Sorting data into groups by comparing two dictionaries
- Designing for safety first: archive before overwrite, report before delete

## How to run
```bash
python backup.py
```
The source folder is `source-test/` and the backup goes to `backup-test/`, both next to the script.

## Output
First run:
```
New: 4
Modified: 0
Skipped (same content): 0
Unchanged: 0
Deleted from source: []
Copied: 0.03 KB
Time: 0.01 s
```

Second run, nothing changed:
```
New: 0
Modified: 0
Skipped (same content): 0
Unchanged: 4
Deleted from source: []
Copied: 0.0 KB
Time: 0.0 s
```

After editing the 4 files:
```
New: 0
Modified: 4
Skipped (same content): 0
Unchanged: 0
Deleted from source: []
Copied: 0.06 KB
Time: 0.03 s
```

## Limitations and next steps
- Add a `--dry-run` mode that shows what would happen without copying.
- Take the source and destination paths as command-line arguments.
- Add a restore command.
- Clean up old archives automatically.

## Resources I used
- [pathlib – Python docs](https://docs.python.org/3/library/pathlib.html)
- [hashlib – Python docs](https://docs.python.org/3/library/hashlib.html)
- [shutil – Python docs](https://docs.python.org/3/library/shutil.html)
- [json – Python docs](https://docs.python.org/3/library/json.html)