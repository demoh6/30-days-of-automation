# Day 03 – Suspicious Link Checker
Part of my #30DaysOfAutomation challenge.

## The problem
Everyone gets links like these: a fake delivery notice, a bank "alert", a prize you never entered. Most scam links leave clues in the URL itself, but only if you know what to look for. A fake domain like `paypa1.com` is easy to miss at a glance.

## What I built
A command-line tool that takes a link and returns a **risk verdict with the reasons behind it**, for example: *"No HTTPS, the domain imitates paypal, and the link contains the word verify."*

It only analyzes the **text** of the link and never connects to the site, so checking a dangerous link is safe.

## How it works
Each check adds points. The total decides the verdict.

| Check | Why it matters | Points |
|-------|----------------|--------|
| No HTTPS | The connection is not encrypted | +1 |
| Suspicious word (`login`, `verify`, `secure`, ...) | Scams push you to act fast | +1 each |
| Domain is an IP address | Real sites use names, not raw IPs | +3 |
| `@` in the link | `google.com@evil.com` really opens `evil.com` | +3 |
| Imitates a known brand | `paypa1` looks like `paypal` | +4 |
| Not a valid URL | Nothing to analyze | +5 |

| Score | Verdict |
|-------|---------|
| 0 | No red flags found |
| 1–2 | Low risk |
| 3–5 | Suspicious |
| 6+ | Dangerous |

### Functions
| Function | What it does |
|----------|--------------|
| `normalize()` | Adds `https://` when the link was typed without a protocol |
| `analyze()` | Runs all checks and returns the findings |
| `total_score()` | Adds up the points |
| `verdict()` | Converts the score into a label |
| `report()` | Prints the verdict and every reason |

## How to run
```bash
python link_checker.py
```
Type a link and press Enter. Press Enter on an empty line to quit.

## Output
```
Enter a URL (empty to quit): www.google.com

URL: www.google.com
Verdict: No red flags found (score: 0 )
```

```
Enter a URL (empty to quit): http://paypa1-secure-login.com/verify

URL: http://paypa1-secure-login.com/verify
Verdict: Dangerous (score: 8 )
   - NO HTTPS (+1)
   - Suspicious word: verify (+1)
   - Suspicious word: secure (+1)
   - Suspicious word: login (+1)
   - Looks like paypal: paypa1 (+4)
```

```
Enter a URL (empty to quit): https://goggle.com/signin

URL: https://goggle.com/signin
Verdict: Suspicious (score: 4 )
   - Looks like google: goggle (+4)
```

## What I learned
- `urllib.parse.urlparse` splits a URL into scheme, host, and path
- `ipaddress.ip_address` with `try/except`, where a success means a problem
- `difflib.SequenceMatcher` to measure how similar two strings are
- Why `hostname` and `netloc` are different, and how the `@` trick exploits it
- Nested data: a list of dictionaries, and looping with `.items()`
- Input handling: normalizing what the user types instead of rejecting it

**A lesson about false alarms:** my first version scored my own website 5 out of 10, because I typed it without `https://` and the tool treated it as an invalid link. A detection tool that cries wolf gets ignored, so I added `normalize()`, which assumes `https` when no protocol is typed. Testing with legitimate input matters as much as testing with bad input.

## Limitations and next steps
- It checks the link text only. It does not follow redirects or look at the page itself.
- The brand list is short, and the similarity threshold (0.8) can occasionally flag harmless words.
- If a link is typed without a protocol, the tool assumes `https`, so it can't tell if it was originally `http`.
- Next: follow redirect chains, check domain age, and expand the brand list.

## Resources I used
- [urllib.parse – Python docs](https://docs.python.org/3/library/urllib.parse.html)
- [ipaddress – Python docs](https://docs.python.org/3/library/ipaddress.html)
- [difflib – Python docs](https://docs.python.org/3/library/difflib.html)