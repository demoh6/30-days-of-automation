"""
Day 1 - #30DaysOfAutomation
A small CLI journal: log what you did today and how long it took.

It is simple on purpose. The idea behind it is the base of most real automations:
read data, change it, save it, and report back, with no manual editing of files.
Every run follows the same flow: INPUT (a task + minutes) -> STORE (journal.json) -> REPORT (summary).

How it works:
    - load_entries()  reads journal.json (returns [] if the file doesn't exist yet)
    - save_entries()  writes the full list back as formatted JSON
    - add_entry()     builds a record {task, minutes, timestamp} and appends it
    - summary()       prints the number of tasks and the total minutes

Usage:
    python journal.py     # asks for a task and its duration, then prints the summary

"""


import json
from datetime import datetime
from pathlib import Path

FILE = Path(__file__).parent / "journal.json"

def load_entries():

    if FILE.exists():
        text = FILE.read_text()
        return json.loads(text)
    else: 
        return []
    
def save_entries(entries):
    text = json.dumps(entries, indent=2)
    FILE.write_text(text)
    
def add_entry(task, minutes):
    timestamp = datetime.now().isoformat()
    entries = load_entries()
    details = {"task": task, "minutes": minutes, "timestamp": timestamp}
    entries.append(details)
    save_entries(entries)

def summary():
    entries = load_entries()
    count = len(entries)
    total = 0
    for m in entries:
        total = total + m["minutes"]
    print ("Total tasks: ", count, "Total minutes: ", total)

task = input("what in ur mind?")
while True:
    try:
        minutes = int(input("How many minutes?"))
        break
    except ValueError:
        print("enter a number")

add_entry(task, minutes)
summary()