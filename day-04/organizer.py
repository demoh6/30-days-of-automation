"""
Day 4 - #30DaysOfAutomation
Safe Folder Organizer: sorts the files of a messy folder into category folders
and can undo the last run.

A messy Downloads folder is a problem everyone has, but a tool that moves your
files must be careful. This one checks the path first, shows a plan before
touching anything, and keeps a record of every run so it can be undone.

How it works:
    - validate_folder()  refuses empty, missing, drive-root, home and system paths
    - plan_moves()       decides where every file goes, without moving anything
    - organize()         shows the plan, asks for confirmation, then moves the files
    - save_session()     writes one JSON file per run (the "memory" used by rollback)
    - rollback()         restores the files of the last run that was not undone yet

Usage:
    python folder_organizer.py "C:\\path\\to\\folder" --dry-run
    python folder_organizer.py "C:\\path\\to\\folder"
    python folder_organizer.py "C:\\path\\to\\folder" --rollback
    python folder_organizer.py                    # asks for the folder
    Add --yes to skip the confirmation question.

    
"""

import argparse
import json
import logging
import shutil
import sys
import uuid
from datetime import datetime
from pathlib import Path



TEMP_EXTENSIONS = {".crdownload", ".part", ".download", ".tmp"}

CATEGORIES = {
    "Images": {".png", ".jpg", ".jpeg", ".jfif", ".webp", ".gif", ".bmp", ".tiff", ".svg", ".ico", ".heic"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".epub"},
    "Office": {".ppt", ".pptx", ".xls", ".xlsx", ".csv", ".ods", ".odp"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".flv", ".m4v"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"},
    "Applications": {".exe", ".msi", ".apk", ".msix", ".appx", ".bat", ".cmd"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
    "Code": {".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".json", ".xml", ".java", ".cpp", ".c", ".cs", ".php", ".sql", ".go", ".rs"},
    "Design": {".psd", ".ai", ".eps", ".fig", ".sketch", ".xd", ".blend", ".obj"},
}
DEFAULT_CATEGORY = "Other"

PROTECTED_PARTS = {"windows", "program files", "program files (x86)", "programdata", "system32", "appdata"}

LOG_DIR_NAME = "logs"
SESSIONS_DIR_NAME = "sessions"

log = logging.getLogger("organizer")



def validate_folder(raw):
    """Return a safe, resolved folder path, or raise ValueError with the reason."""
    raw = raw.strip().strip('"').strip("'")
    if not raw:
        raise ValueError("No folder given. Refusing to guess which folder you meant.")

    folder = Path(raw).expanduser().resolve()

    if not folder.is_dir():
        raise ValueError(f"Folder not found: {folder}")
    if folder == Path(folder.anchor) or folder == Path.home():
        raise ValueError(f"Refusing to organize a drive root or your home folder: {folder}")
    if any(part.lower() in PROTECTED_PARTS for part in folder.parts):
        raise ValueError(f"Refusing to organize a system folder: {folder}")

    return folder


def is_inside(path, folder):
    """True if path is located somewhere inside folder."""
    return folder in Path(path).resolve().parents


def confirm(question, assume_yes):
    if assume_yes:
        return True
    return input(f"{question} [y/N]: ").strip().lower() == "y"



def setup_logging(folder):
    """Create the logs folder and start logging. Called only when we really write."""
    logs_dir = folder / LOG_DIR_NAME
    sessions_dir = logs_dir / SESSIONS_DIR_NAME
    sessions_dir.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(logs_dir / "organizer.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(message)s"))

    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler], force=True)
    return sessions_dir



def get_category(file):
    extension = file.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category
    return DEFAULT_CATEGORY


def unique_path(path, reserved):
    """Return a path that does not exist yet and is not already planned."""
    candidate = path
    counter = 1
    while candidate.exists() or str(candidate).lower() in reserved:
        candidate = path.with_name(f"{path.stem} ({counter}){path.suffix}")
        counter += 1
    return candidate


def plan_moves(folder):
    """Decide where every file goes. Moves nothing."""
    moves = []
    skipped = []
    reserved = set()
    this_script = Path(__file__).resolve()

    for file in sorted(folder.iterdir()):
        if not file.is_file():
            continue
        if file.resolve() == this_script:
            skipped.append((file.name, "this script"))
            continue
        if file.name.startswith("."):
            skipped.append((file.name, "hidden file"))
            continue
        if file.suffix.lower() in TEMP_EXTENSIONS:
            skipped.append((file.name, "temporary download"))
            continue

        destination = unique_path(folder / get_category(file) / file.name, reserved)
        reserved.add(str(destination).lower())
        moves.append((file, destination))

    return moves, skipped


def print_plan(moves, skipped):
    counts = {}
    for _, destination in moves:
        category = destination.parent.name
        counts[category] = counts.get(category, 0) + 1

    for category, count in sorted(counts.items()):
        print(f"  {category}: {count} file(s)")
    for name, reason in skipped:
        print(f"  skipped: {name} ({reason})")



def save_session(sessions_dir, session_id, folder, done):
    """Write one JSON file describing the moves of this run."""
    if not done:
        return
    now = datetime.now()
    data = {
        "session": session_id,
        "created": now.isoformat(timespec="seconds"),
        "folder": str(folder),
        "rolled_back": False,
        "moves": [{"from": str(source), "to": str(destination)} for source, destination in done],
    }
    name = f"{now.strftime('%Y%m%d_%H%M%S_%f')}_{session_id[:8]}.json"
    (sessions_dir / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def find_last_session(sessions_dir):
    """Return (path, data) of the newest session that was not rolled back yet."""
    if not sessions_dir.is_dir():
        return None, None
    for path in sorted(sessions_dir.glob("*.json"), reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"Warning: could not read {path.name}, skipping it.")
            continue
        if not data.get("rolled_back"):
            return path, data
    return None, None



def organize(folder, args):
    moves, skipped = plan_moves(folder)
    if not moves:
        print("Nothing to organize.")
        return

    print(f"Plan for {folder}:")
    print_plan(moves, skipped)

    if args.dry_run:
        print("\nDry run: nothing was moved and nothing was written.")
        return
    if not confirm(f"\nMove {len(moves)} file(s)?", args.yes):
        print("Cancelled. Nothing was moved.")
        return

    sessions_dir = setup_logging(folder)
    session_id = uuid.uuid4().hex
    done = []
    failed = 0

    log.info("START session=%s folder=%s", session_id, folder)
    try:
        for source, destination in moves:
            try:
                destination.parent.mkdir(exist_ok=True)
                shutil.move(str(source), str(destination))
                done.append((source, destination))
                log.info("MOVED %s -> %s", source.name, destination.parent.name)
            except Exception as error:
                failed += 1
                log.error("FAILED %s: %s", source.name, error)
    finally:
       
        save_session(sessions_dir, session_id, folder, done)

    for name, reason in skipped:
        log.info("SKIPPED %s (%s)", name, reason)
    log.info("DONE moved=%d skipped=%d failed=%d", len(done), len(skipped), failed)


def rollback(folder, args):
    sessions_dir = folder / LOG_DIR_NAME / SESSIONS_DIR_NAME
    session_path, data = find_last_session(sessions_dir)
    if data is None:
        print("Nothing to roll back.")
        return

    print(f"Last run: {data['created']} ({len(data['moves'])} file(s) moved)")

    if args.dry_run:
        for move in data["moves"]:
            print(f"  would restore: {Path(move['to']).name} -> {Path(move['from']).parent}")
        print("\nDry run: nothing was restored and nothing was written.")
        return
    if not confirm("Restore these files?", args.yes):
        print("Cancelled. Nothing was restored.")
        return

    setup_logging(folder)
    restored = skipped = failed = 0
    touched_dirs = set()

    log.info("ROLLBACK START session=%s", data["session"])
    for move in reversed(data["moves"]):
        destination, source = Path(move["to"]), Path(move["from"])
        try:
            if not (is_inside(destination, folder) and is_inside(source, folder)):
                skipped += 1
                log.warning("SKIPPED %s (path is outside the organized folder)", destination.name)
                continue
            if not destination.is_file():
                skipped += 1
                log.warning("SKIPPED %s (file not found, maybe moved or deleted)", destination.name)
                continue
            if source.exists():
                skipped += 1
                log.warning("SKIPPED %s (original path is occupied)", source.name)
                continue

            source.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(destination), str(source))
            touched_dirs.add(destination.parent)
            restored += 1
            log.info("RESTORED %s", source.name)
        except Exception as error:
            failed += 1
            log.error("FAILED %s: %s", destination.name, error)

    for category_dir in touched_dirs:
        try:
            category_dir.rmdir()
        except OSError:
            pass

    data["rolled_back"] = True
    data["rolled_back_at"] = datetime.now().isoformat(timespec="seconds")
    session_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("ROLLBACK DONE restored=%d skipped=%d failed=%d", restored, skipped, failed)



def parse_args():
    parser = argparse.ArgumentParser(description="Sort a messy folder into category folders, and undo it if needed.")
    parser.add_argument("path", nargs="?", help="folder to organize (asked interactively if omitted)")
    parser.add_argument("--rollback", action="store_true", help="undo the last run")
    parser.add_argument("--dry-run", action="store_true", help="show what would happen, change nothing")
    parser.add_argument("--yes", "-y", action="store_true", help="skip the confirmation question")
    return parser.parse_args()


def main():
    args = parse_args()
    raw = args.path if args.path is not None else input("Folder to organize: ")

    try:
        folder = validate_folder(raw)
    except ValueError as error:
        print(f"Error: {error}")
        return 1

    if args.rollback:
        rollback(folder, args)
    else:
        organize(folder, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())