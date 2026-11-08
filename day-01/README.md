# Day 01 – Python Basics for Automation + CLI Journal
Part of my #30DaysOfAutomation challenge.

## What I learned today
Before automating anything, I needed the basic building blocks. Today I used them in one small tool:

| Concept | What it does | Where I used it |
|---------|--------------|-----------------|
| `pathlib` | Handles file paths and reads/writes files | `FILE.exists()`, `read_text()`, `write_text()` |
| `json` | Converts between Python data and text | `json.loads()` / `json.dumps()` |
| `datetime` | Gives the current date and time | Timestamp on every entry |
| Dictionaries | Store one record as `key: value` pairs | `{"task", "minutes", "timestamp"}` |
| Lists + `for` loop | Hold many records and go through them | Counting tasks and summing minutes |
| `try / except` | Handles errors without crashing | Re-asks if the minutes aren't a number |
| Functions | Split the code into small, testable pieces | `load`, `save`, `add`, `summary` |

**A bug worth remembering:** a relative path like `Path("journal.json")` is resolved from the folder where the terminal is running, not from where the script lives. The fix is `Path(__file__).parent / "journal.json"`, which always points next to the script. This will matter a lot when scripts run on schedulers and servers.

**My takeaway:** every automation follows the same flow: **input → store → report**. This journal is a tiny version of that.

## Mini project: CLI journal
`journal.py` asks what you did and how long it took, saves it to `journal.json`, and prints a summary. The file is created automatically on the first run.

Each entry looks like this:

```json
{
  "task": "Learning Python",
  "minutes": 40,
  "timestamp": "2026-11-08T10:00:00.123456"
}
```

### How it works
| Function | What it does |
|----------|--------------|
| `load_entries()` | Reads `journal.json`, returns `[]` if it doesn't exist |
| `save_entries()` | Writes the full list back as formatted JSON |
| `add_entry()` | Builds a `{task, minutes, timestamp}` record and appends it |
| `summary()` | Prints the number of tasks and the total minutes |

### How to run
```bash
python journal.py
```

### Output
```
what in ur mind?Learning Python
How many minutes?40
Total tasks:  1 Total minutes:  40
```

Run it again and the entries add up:

```
what in ur mind?Reading
How many minutes?20
Total tasks:  2 Total minutes:  60
```

If you type letters instead of a number, it asks again instead of crashing.

## Resources I used
- [pathlib – Python docs](https://docs.python.org/3/library/pathlib.html)
- [json – Python docs](https://docs.python.org/3/library/json.html)
- [datetime – Python docs](https://docs.python.org/3/library/datetime.html)
- [Virtual environments – Python tutorial](https://docs.python.org/3/tutorial/venv.html)