# Site helpers

Three commands for adding content, run from the repository root with Python 3. Each one has `--help` and a `--dry-run` that prints exactly what
would change and writes nothing. None of them overwrites an existing file or entry, commits, pushes or builds the site.

`bin/sitelib.py` holds the helpers they share, and `bin/templates/project.md` is the template for new project pages.

## Add a photo

```bash
python3 bin/add_photo.py ~/Pictures/IMG_0042.jpg --title "old town bridge" --city Tubingen --strip-gps
```

- Copies the image to `assets/img/photo/old_town_bridge.jpg` (the original is not changed).
- Appends `title`, `city`, `date`, `image`, `width` and `height` to the end of `_data/gallery.yml`.
- Makes the grid thumbnail `assets/img/photo/thumbs/old_town_bridge.jpg`.
- Prints the page URL, here `/gallery/old-town-bridge/`.

The date comes from the photo's EXIF, or the file's modified time if there is none. The city is matched against `_data/gallery_cities.yml` ignoring
case and accents, so `Tubingen` becomes `Tübingen`. If `--city` is left out, `--geocode` looks it up from the photo's GPS position through
OpenStreetMap Nominatim, which is the only network request the script makes. Otherwise the script asks for it.

If the photo has GPS data, the script warns you and asks before publishing it. `--strip-gps` removes the GPS tags from the published copy. For a JPEG
this is lossless. Each run also lists the photos already in the gallery that still contain GPS data. Pillow (`pip install Pillow`) is needed for the
thumbnail. Without it, the photo is still added and you run `python3 bin/gallery_thumbs.py` later.

## Add a project

```bash
python3 bin/add_project.py "Lumen" --description "Ambient light sensing for night cyclists" --category research --logo ~/lumen.png
```

- Creates `_projects/6_project.md` (the next number) from `bin/templates/project.md`, with a placeholder body.
- Copies the logo to `assets/img/lumen/lumen_logo.png` and sets `logo:` in the front matter. `--img` does the same for the card image as
  `lumen_card.<ext>`.

By default the project goes last in its category. `--order N` puts it at position N. If N is already taken, the command stops, unless you add
`--shift`, which moves the projects at N and after down by one by editing their `order:` lines. `--hidden` adds `published: false`.

## Add a paper

```bash
python3 bin/add_paper.py 10.1109/IEMTRONICS51293.2020.9216383 --selected
```

This appends one normalized entry to `_bibliography/papers.bib`. (That DOI is the paper already in the file, so running this example just reports
the duplicate.) The source can also be an arXiv ID or URL (`2101.00001`,
`https://arxiv.org/abs/2101.00001`) or a local `.bib` file, which adds every entry in it.

Entries are normalized to the style of the existing one: `Last, First` authors, a `pdf` link, `bibtex_show={false}` and, with `--selected`,
`selected={true}`. The key is `lastnameYEARfirstword` unless you pass `--key`. Entries already in the file (same DOI, arXiv ID or title) are skipped.
The script warns when the author list lacks the name highlighted on the page (`scholar.first_name`/`last_name` in `_config.yml`). It only contacts
doi.org, api.crossref.org and export.arxiv.org.

## What's left to do by hand

1. Review the change: `git status`, `git diff`. For a project, write the page body. For a paper, check the venue name and the title's capitalization.
2. Optionally preview it locally with `bundle exec jekyll serve`.
3. Commit and push. Each script prints the `git add` line for the files it changed.
