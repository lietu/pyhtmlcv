#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyHtmlCv is a tool to that can be used to generate HTML CVs from a
simple JSON configuration.

:copyright: (c) 2012-2019 Janne Enberg
:license: BSD
"""

from argparse import ArgumentParser, ArgumentTypeError
import codecs
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import json

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

import re
import sass
import six
import shutil
import sys
from time import sleep

TEMPLATE_PATH = Path("templates")


def str2bool(value):
    """
    Convert CLI args to boolean
    :param str value:
    :return bool:
    """
    if value.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif value.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise ArgumentTypeError("Boolean value expected.")


def get_last_change(path):
    """
    Figure out when the given path has last changed, recursively if a directory
    """
    last_changed = path.stat().st_mtime

    if path.is_dir():
        for entry in path.glob("**/*"):
            entry_changed = entry.stat().st_mtime
            if entry_changed > last_changed:
                last_changed = entry_changed

    return last_changed


def run(options):
    """
    Generate the CV page from the source + template
    """

    try:
        with codecs.open(options.source, encoding="utf-8") as f:
            config = json.load(f)
    except ValueError as e:
        print("Error parsing config {}.".format(options.source))
        print("")
        raise
    except IOError as e:
        print("Configuration file not found: {}".format(options.source))
        print("")
        raise

    validate_config(config)
    process_config(config)
    generate_cv(options.target, options.template, config)


def generate_cv(destination, template, config):
    # Get the template
    template_path = str(TEMPLATE_PATH / template)
    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template("index.html")

    # Generate a few variables for the template
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S %z")
    year = now.strftime("%Y")
    navigation = generate_navigation(config)

    # Render the template into HTML
    html = template.render(
        name=config["name"],
        contact=config["contact"],
        sections=config["sections"],
        navigation=navigation,
        now=current_time,
        year=year,
    )

    # Make sure that the destination path is deleted first
    dst_path = Path(destination)
    if dst_path.exists():
        shutil.rmtree(destination)
    shutil.copytree(template_path, destination)

    # Compile Sass/SCSS
    scss_files = []
    for entry in dst_path.glob("**/*.scss"):
        scss_files.append(entry)
        entry_name = entry.name
        if entry_name.endswith(".scss") and not entry_name.startswith("_"):
            entry_str = str(entry)
            compiled = sass.compile(filename=entry_str)
            entry_css = Path(entry_str[:-5] + ".css")
            with entry_css.open("w", encoding="utf-8") as f:
                f.write(compiled)
            print("Compiled {} to {}".format(entry, entry_css))

    # Delete unnecessary files after compilation
    for entry in scss_files:
        entry.unlink()

    # And any left over empty directories
    for entry in reversed(list(dst_path.rglob("*"))):
        if entry.exists() and entry.is_dir():
            empty = True
            for _ in entry.iterdir():
                empty = False
                break

            if empty:
                entry.rmdir()

    # Write the result HTML
    full_path = Path(destination) / "index.html"
    with full_path.open("w", encoding="utf-8") as f:
        f.write(html)

    print("Generated CV HTML to {}".format(full_path))


def validate_config(config):
    error = False

    if "name" not in config:
        print('Missing name definition, e.g. { "name": "Janne Enberg", ' "... }")
        error = True

    if "contact" not in config:
        print(
            "Missing contact definition, e.g. { ..., "
            '"contact": "+1 (2) 345 678 | contact@example.com", ... }'
        )
        error = True

    if "sections" not in config:
        print("Missing sections definition, e.g. { ..., " '"sections": [ ... ] }')
        error = True
    else:
        for section in config["sections"]:
            # String sections need no other validation
            if isinstance(section, six.string_types):
                continue

            if "title" not in section:
                print(
                    "Missing title from section definition, , "
                    'e.g. { ..., "sections": [ {"title": "Section '
                    'title", ...} ] }'
                )
                print("Found: {}".format(section))
                error = True

            if (
                "fields" not in section
                and "large" not in section
                and "largeList" not in section
            ):
                print(
                    "No fields, largeList or large definition for "
                    "section, , "
                    'e.g. { ..., "sections": [ {..., '
                    '"large": "Yadi yadi yada", ...} ] }'
                )
                error = True

            if "fields" in section:
                for field in section["fields"]:
                    if not isinstance(field, list) or len(field) != 2:
                        print(
                            "Invalid field definition, "
                            "it should have two items, e.g. { ..., "
                            '"sections": [ {..., "fields": [ ["Label",'
                            ' "Value"], ... }, ... ] }'
                        )
                        error = True

    if error:
        print("")
        print("Please fix errors in configuration file.")
        sys.exit(1)


def process_config(config):
    """
    Process the configuration from the readable format to a more useful format
    """

    # Process sections
    for index, section in enumerate(config["sections"]):
        # String sections will be converted to type = heading
        if isinstance(section, six.string_types):
            if section == "-":
                config["sections"][index] = {"type": "page-break"}

            else:
                config["sections"][index] = {"type": "heading", "title": section}

            continue

        # The rest are just normal sections
        section["type"] = "normal"

        # Convert ["Label", "Value"] to {"label": "Label",
        # "value": "Value"}
        if "fields" in section:
            fields = []

            for fieldColumns in section["fields"]:
                fields.append({"label": fieldColumns[0], "value": fieldColumns[1]})

            section["fields"] = fields

        # Convert arrays in "largeList" field to <ul> -lists in "large"
        if "largeList" in section:
            section["large"] = (
                "<ul><li>" + "</li><li>".join(section["largeList"]) + "</li></ul>"
            )

            del section["largeList"]

    heading = config["mainHeading"]

    main_heading = {"type": "heading", "title": heading}

    config["sections"] = [main_heading] + config["sections"]


def generate_navigation(config):
    i = 1
    nav = {"headings": []}

    for _, section in enumerate(config["sections"]):
        # Page breaks don't need navigation
        if section["type"] == "page-break":
            continue

        name = section["title"]
        section["id"] = make_id(name, i)

        if section["type"] == "heading":
            nav[name] = [section]

            nav["headings"].append(name)

            heading = name
        else:
            nav[heading].append(section)

        i += 1

    return nav


def make_id(text, index):
    # Replace characters not valid in IDs
    text = re.sub(r"[^0-9a-zA-Z\-_.:]", "-", text)

    # Text must not begin with a number
    if re.match(r"^[0-9]", text):
        text = "id-{}-{}".format(text, index)

    return text


def main():
    ap = ArgumentParser()
    ap.add_argument("--source", default="cv.json", type=str, help="CV JSON source")
    ap.add_argument(
        "--target", type=str, help="Target directory, defaults to generated/<source>/"
    )
    ap.add_argument(
        "--template",
        type=str,
        default="default",
        help="One of the subfolders of templates/",
    )
    ap.add_argument(
        "--watch",
        type=str2bool,
        nargs="?",
        const=True,
        default=False,
        help="Keep watching for changes",
    )

    options = ap.parse_args()
    if not options.target:
        options.target = str(Path("generated") / options.source)

    if options.watch:
        print("Press CTRL+C to stop monitoring for changes")

        last_change = 0
        source_path = Path(options.source)
        template_path = TEMPLATE_PATH / options.template
        while True:
            changes = False
            source_change = get_last_change(source_path)
            if source_change > last_change:
                changes = True

            template_change = get_last_change(template_path)
            if template_change > last_change:
                changes = True

            if changes:
                last_change = max(template_change, source_change)
                try:
                    run(options)
                except Exception as e:
                    print(e)
                except SystemExit:
                    pass

            sleep(0.25)
    else:
        run(options)


if __name__ == "__main__":
    main()
