"""
Day 2 - #30DaysOfAutomation
An incremental backup tool: copies only the files that are new or changed.

Copying a whole folder every time wastes time and space, and a plain copy
overwrites the previous version. This tool remembers what it already backed up
and keeps old versions, so a bad edit never destroys your only good copy.

How it works:
    - scan()          lists every file in the source with its size and modified time
    - load_manifest() reads the record of the last backup (manifest.json)
    - compare()       sorts files into new / modified / unchanged / deleted
    - run_backup()    copies new and modified files, then updates the manifest
    - file_hash()     confirms a "modified" file really changed (SHA-256 of its content)

Safety rules:
    - A modified file's old version is moved to _archive/<timestamp>/ before it is replaced
    - Files deleted from the source are reported, never deleted from the backup
    - If only the timestamp changed but the content is identical, the file is skipped

Usage:
    python backup.py

"""


from pathlib import Path
import hashlib
import json
import shutil
import datetime
import time

SOURCE = Path(__file__).parent / "source-test"
DEST = Path(__file__).parent / "backup-test"
MANIFEST_FILE = DEST / "manifest.json"

def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
        return h.hexdigest()

def scan(folder):
    result = { }
    for p in folder.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(folder).as_posix()
        info = p.stat()
        result[rel] = {"size": info.st_size, "mtime": info.st_mtime}
    return result

def load_manifest():
    if MANIFEST_FILE.exists():
         text = MANIFEST_FILE.read_text()
         return json.loads(text)
    return {}    

def save_manifest(manifest):
    DEST.mkdir(exist_ok=True)
    text = json.dumps(manifest, indent=2)
    MANIFEST_FILE.write_text(text)

def compare(current, manifest):
    result = {"new": [], "modified": [], "unchanged": [], "deleted": []}
    for rel in current:
        if rel not in manifest:
            result["new"].append(rel)
        elif current[rel] != manifest[rel]:
            result["modified"].append(rel)
        else:
            result["unchanged"].append(rel)
            
    for rel in manifest:
        if rel not in current:
            result["deleted"].append(rel)
    return result

def run_backup():
    start = time.time()
    current = scan(SOURCE)
    manifest = load_manifest()
    changes = compare(current, manifest)
    to_copy = changes["new"] + changes["modified"]
    total_size = 0
    skipped = 0
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    for rel in to_copy:
        src = SOURCE / rel
        dst = DEST / rel

        if rel in changes["modified"] and dst.exists():
            if file_hash(src) == file_hash(dst):
                skipped = skipped + 1
                continue

        dst.parent.mkdir(parents=True, exist_ok=True)

        if rel in changes["modified"] and dst.exists():
            archived = DEST / "_archive" / stamp / rel
            archived.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(dst, archived)

        shutil.copy2(src, dst)
        total_size = total_size + current[rel]["size"]

    save_manifest(current)

    print("New:", len(changes["new"]))
    print("Modified:", len(changes["modified"]))
    print("Skipped (same content):", skipped)
    print("Unchanged:", len(changes["unchanged"]))
    print("Deleted from source:", changes["deleted"])
    print("Copied:", round(total_size / 1024, 2), "KB")
    print("Time:", round(time.time() - start, 2), "s")

run_backup()

