#!/usr/bin/env python3
"""Create a new project page in one step.

Writes _projects/N_project.md (N = the next number after the highest existing
one) from bin/templates/project.md, with the title, description, category and
order filled in. Lines of the template whose value is left empty (img, logo,
published) are dropped.

  order       defaults to the highest order in that category plus one. A taken
              --order is an error, unless --shift, which moves the projects at
              that order or above in the category down by one (their files are
              edited as text: only the `order:` line changes).
  importance  the highest importance across all projects plus one.
  --logo/--img are copied to assets/img/<slug>/<slug>_logo.<ext> and _card.<ext>
              and set in the front matter. Without either, the listing shows the title's first letter.
  --hidden    adds `published: false`, which keeps the page out of the site.

No network access.
"""
import argparse
import os
import re
import string
import sys

sys.dont_write_bytecode = True  # importing the helper below must not leave bin/__pycache__
import sitelib
from sitelib import ROOT, die, warn, rel, slugify, yaml_scalar

PROJECTS = os.path.join(ROOT, "_projects")
TEMPLATE = os.path.join(ROOT, "bin", "templates", "project.md")
CATEGORIES = ("products", "research")  # as in _includes/projects_grid.liquid


def front_matter(text):
    m = re.match(r"---\n(.*?\n)---\n", text, re.S)
    return m.group(1) if m else ""


def field(fm, key):
    m = re.search(rf"^{key}:[ \t]*(.*?)[ \t]*(?:#.*)?$", fm, re.M)
    return m.group(1).strip("\"'") if m else None


def load_projects():
    out = []
    for name in sorted(os.listdir(PROJECTS)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(PROJECTS, name)
        fm = front_matter(open(path, encoding="utf-8").read())
        order, imp = field(fm, "order"), field(fm, "importance")
        out.append({
            "path": path,
            "title": field(fm, "title") or "",
            "category": field(fm, "category"),
            "order": int(order) if order and order.lstrip("-").isdigit() else None,
            "importance": int(imp) if imp and imp.lstrip("-").isdigit() else None,
        })
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("title", help="project title")
    ap.add_argument("--description", required=True, help="one-line description shown in the listing")
    ap.add_argument("--category", required=True, help="products or research")
    ap.add_argument("--order", type=int, help="position in the category (default: last)")
    ap.add_argument("--shift", action="store_true", help="if --order is taken, move that project and the ones after it down by one")
    ap.add_argument("--logo", help="logo image to copy into assets/img/<project-slug>/ (shown in the listing)")
    ap.add_argument("--img", help="card image to copy into assets/img/<project-slug>/")
    ap.add_argument("--hidden", action="store_true", help="add `published: false` (page not built)")
    ap.add_argument("--dry-run", action="store_true", help="print what would change and write nothing")
    a = ap.parse_args()

    title = " ".join(a.title.split())
    desc = " ".join(a.description.split())
    if not title:
        die("the title is empty")
    if not desc:
        die("the description is empty")
    if a.category not in CATEGORIES:
        die(f"category must be one of {', '.join(CATEGORIES)}, got '{a.category}'")
    if a.order is not None and a.order < 1:
        die("--order must be 1 or more")
    if a.shift and a.order is None:
        die("--shift needs --order")
    slug = slugify(title, sep="")
    if not slug:
        die("the title has no letters or digits to make a slug from")
    for f in (a.logo, a.img):
        if f and not os.path.isfile(f):
            die(f"no such file: {f}")

    projects = load_projects()
    for p in projects:
        if slugify(p["title"], sep="") == slug:
            die(f"'{title}' collides with the existing project '{p['title']}' ({rel(p['path'])}); choose another title")

    same = [p for p in projects if p["category"] == a.category]
    orders = {}
    for p in same:
        if p["order"] is not None:
            orders.setdefault(p["order"], []).append(p)
    for o, ps in sorted(orders.items()):
        if len(ps) > 1:
            warn(f"{a.category}: order {o} is shared by " + ", ".join(os.path.basename(p["path"]) for p in ps))

    shifts = []
    if a.order is None:
        order = max(orders, default=0) + 1
    else:
        order = a.order
        if order in orders:
            if not a.shift:
                taken = ", ".join(f"{os.path.basename(p['path'])} ({p['title']})" for p in orders[order])
                die(f"order {order} in {a.category} is taken by {taken}; pick another or pass --shift")
            shifts = sorted((p for p in same if p["order"] is not None and p["order"] >= order), key=lambda p: p["order"])
    importance = max((p["importance"] for p in projects if p["importance"] is not None), default=0) + 1

    nums = [int(m.group(1)) for n in os.listdir(PROJECTS) if (m := re.fullmatch(r"(\d+)_project\.md", n))]
    path = os.path.join(PROJECTS, f"{max(nums, default=0) + 1}_project.md")

    # named like the existing ones (medi_logo.jpg, freqnav_card.png); one copy if both are the same file
    copies, fm_paths = [], {}
    for key, f, suffix in (("logo", a.logo, "logo"), ("img", a.img, "card")):
        if not f:
            continue
        done = [d for s, d in copies if os.path.samefile(s, f)]
        dst = done[0] if done else os.path.join(ROOT, "assets", "img", slug, f"{slug}_{suffix}{os.path.splitext(f)[1].lower()}")
        if not done:
            if os.path.exists(dst):
                die(f"{rel(dst)} already exists; not overwriting")
            copies.append((f, dst))
        fm_paths[key] = rel(dst).replace(os.sep, "/")

    tpl = string.Template(open(TEMPLATE, encoding="utf-8").read())
    text = tpl.substitute(
        title=yaml_scalar(title),
        description=yaml_scalar(desc),
        description_text=desc,
        img=fm_paths.get("img", ""),
        logo=fm_paths.get("logo", ""),
        importance=importance,
        order=order,
        category=a.category,
        published="false # hidden from the projects page; delete this line to restore" if a.hidden else "",
    )
    head, body = text.split("\n---\n", 1)
    head = re.sub(r"^(img|logo|published):[ \t]*\n", "", head + "\n", flags=re.M).rstrip("\n")
    text = head + "\n---\n" + body

    tag = "would " if a.dry_run else ""
    print(f"{tag}create {rel(path)}:")
    print("".join("    " + ln + "\n" for ln in front_matter(text).rstrip("\n").split("\n")), end="")
    for s, d in copies:
        print(f"{tag}copy {s} -> {rel(d)}")
    for p in shifts:
        print(f"{tag}change {rel(p['path'])} ({p['title']}): order {p['order']} -> {p['order'] + 1}")
    if a.dry_run:
        print("dry run: nothing written")
        return

    if os.path.exists(path):
        die(f"{rel(path)} already exists; not overwriting")
    for p in shifts:  # check all before writing any
        if not re.search(r"^order:[ \t]*\d+", open(p["path"], encoding="utf-8").read(), re.M):
            die(f"can't find the order line in {rel(p['path'])}")
    for s, d in copies:
        sitelib.write_new(d, open(s, "rb").read(), False)
    for p in shifts:
        t = open(p["path"], encoding="utf-8").read()
        t = re.sub(r"^order:([ \t]*)\d+", lambda m: f"order:{m.group(1)}{p['order'] + 1}", t, count=1, flags=re.M)
        open(p["path"], "w", encoding="utf-8").write(t)
    sitelib.write_new(path, text, False)

    changed = [rel(path)] + [rel(d) for _, d in copies] + [rel(p["path"]) for p in shifts]
    print()
    print(f"created '{title}' ({a.category}, order {order}{', hidden' if a.hidden else ''}): {rel(path)}")
    if shifts:
        print(f"shifted {len(shifts)} project(s) down by one")
    print(f"next: write the page body in {rel(path)}, then git add {' '.join(changed)} && git commit, and push")


if __name__ == "__main__":
    main()
