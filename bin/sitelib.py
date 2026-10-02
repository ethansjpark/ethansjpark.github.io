"""Small helpers shared by bin/add_photo.py, bin/add_project.py and bin/add_paper.py.

Standard library only. Not a command; import it.
"""
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_AGENT = "ethansjpark.github.io site helper (https://github.com/ethansjpark/ethansjpark.github.io)"
TIMEOUT = 20

sys.stdout.reconfigure(line_buffering=True)  # keep stdout and stderr lines in order when piped


def die(msg):
    """One-line error and exit status 1."""
    sys.exit(f"error: {msg}")


def warn(msg):
    print(f"warning: {msg}", file=sys.stderr)


def rel(path):
    return os.path.relpath(path, ROOT)


def fold(s):
    """Lowercase with accents removed, for matching ("Tubingen" == "Tübingen")."""
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).casefold().strip()


def slugify(s, sep="_"):
    """ascii, lowercase, runs of anything else -> sep."""
    return re.sub(r"[^a-z0-9]+", sep, fold(s)).strip(sep)


def yaml_scalar(s):
    """A YAML value as written in the data files: plain when safe, else double-quoted."""
    s = str(s)
    plain = (
        s
        and s == s.strip()
        and not re.search(r": |\s#|[\n\t]|:$", s)
        and s[0] not in "!&*-?{}[]|>'\"%@`#,"
        and s.lower() not in ("true", "false", "yes", "no", "on", "off", "null", "~")
        and not re.fullmatch(r"[-+.0-9eE:_]+", s)
    )
    return s if plain else json.dumps(s, ensure_ascii=False)


def is_tty():
    return sys.stdin.isatty()


def ask(prompt):
    try:
        return input(prompt)
    except EOFError:
        return ""


class OffListRedirect(Exception):
    pass


def http_get(url, accept=None, hosts=None):
    """GET with a timeout and a descriptive User-Agent; no retries. Returns (status, text).
    With hosts, a redirect to any other host is not followed (raises OffListRedirect)."""
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept

    class Guard(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, hdrs, newurl):
            host = urllib.parse.urlsplit(newurl).hostname
            if hosts and host not in hosts:
                raise OffListRedirect(host)
            return super().redirect_request(req, fp, code, msg, hdrs, newurl)

    opener = urllib.request.build_opener(Guard)
    req = urllib.request.Request(url, headers=headers)
    try:
        with opener.open(req, timeout=TIMEOUT) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        reason = getattr(e, "reason", e)
        raise ConnectionError(f"{urllib.parse.urlsplit(url).hostname}: {reason}") from None


def append_text(path, block, dry_run):
    """Append block to a text file, keeping one blank line between it and what's there."""
    text = open(path, encoding="utf-8").read()
    sep = "" if not text else ("\n" if text.endswith("\n\n") else ("\n" if text.endswith("\n") else "\n\n"))
    if not dry_run:
        with open(path, "a", encoding="utf-8") as f:
            f.write(sep + block)
    return sep + block


def write_new(path, data, dry_run):
    """Create a file that must not exist yet (never overwrites)."""
    if os.path.exists(path):
        die(f"{rel(path)} already exists; not overwriting")
    if dry_run:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = "xb" if isinstance(data, bytes) else "x"
    with open(path, mode, **({} if isinstance(data, bytes) else {"encoding": "utf-8"})) as f:
        f.write(data)

