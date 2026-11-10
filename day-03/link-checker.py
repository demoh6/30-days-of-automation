"""
Day 3 - #30DaysOfAutomation
A suspicious link checker: paste a link, get a risk verdict with clear reasons.

Scam links reach everyone: a fake delivery notice, a bank "alert", a prize you
never entered. Most of them leave visible clues in the URL itself, if you know
where to look. This tool looks for those clues for you and explains each one.

It only analyzes the TEXT of the link. It never connects to the site,
so checking a dangerous link is safe.

How it works:
    - normalize()    adds https:// when the link was typed without a protocol
    - analyze()      runs the checks and returns a list of findings with points
    - total_score()  adds up the points
    - verdict()      turns the score into: No red flags / Low risk / Suspicious / Dangerous
    - report()       prints the verdict and the reason behind every point

Checks:
    - No HTTPS                          +1
    - Suspicious words (login, verify)  +1 each
    - Domain is an IP address           +3
    - "@" in the link (hides the real domain) +3
    - Domain imitates a known brand (paypa1 vs paypal) +4
    - Not a valid URL                   +5

Usage:
    python link_checker.py     # type a link, press Enter on an empty line to quit

"""



from urllib.parse import urlparse
import ipaddress
import difflib

SUSPICIOUS_WORDS = ["confirm", "update", "verify", "secure", "login", "account"]
KNOWN_BRANDS = ["google", "paypal", "apple", "amazon", "facebook", "microsoft", "netflix"]


def normalize(url):
    url = url.strip()
    if "://" not in url:
        url = "https://" + url
    return url


def analyze(url):
    url = normalize(url)
    parsed = urlparse(url)
    host = parsed.hostname
    findings = []


    if not host or "." not in host:
        findings.append({"Not a valid URL": 5})
        return findings

    if parsed.scheme != "https":
        findings.append({"NO HTTPS": 1})

    try:
        ipaddress.ip_address(host)
        findings.append({"Domain is an IP address": 3})
    except ValueError:
        pass

    if "@" in parsed.netloc:
        findings.append({"Contains @ (hides the real domain)": 3})

    link = url.lower()
    for word in SUSPICIOUS_WORDS:
        if word in link:
            findings.append({"Suspicious word: " + word: 1})

    parts = host.replace("-", ".").split(".")
    for part in parts:
        for brand in KNOWN_BRANDS:
            score = difflib.SequenceMatcher(None, part, brand).ratio()
            if score >= 0.8 and part != brand:
                findings.append({"Looks like " + brand + ": " + part: 4})

    return findings


def total_score(findings):
    total = 0
    for finding in findings:
        for reason, points in finding.items():
            total = total + points
    return total


def verdict(total):
    if total >= 6:
        return "Dangerous"
    elif total >= 3:
        return "Suspicious"
    elif total >= 1:
        return "Low risk"
    else:
        return "No red flags found"


def report(url):
    findings = analyze(url)
    total = total_score(findings)
    print("")
    print("URL:", url)
    print("Verdict:", verdict(total), "(score:", total, ")")
    for finding in findings:
        for reason, points in finding.items():
            print("   -", reason, "(+" + str(points) + ")")


while True:
    text = input("Enter a URL (empty to quit): ").strip()
    if not text:
        break
    report(text)