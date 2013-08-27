#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyHtmlCv is a tool to that can be used to generate HTML CVs from a
    simple JSON configuration.

    :copyright: (c) 2012 Janne Enberg
    :license: BSD
"""

import json
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import distutils.core
import os
import sys
import codecs
import re


class pyhtmlcv(object):
    """CV Generator main class"""

    def main(self):
        """Process the invokation of cvgen"""

        if len(sys.argv) != 2:
            self.usage()

        file = sys.argv[1]
        if not os.path.exists(file):
            print "File not found %s" % file
            self.usage()

        fileHandle = open(file)

        try:
            config = json.load(fileHandle)
        except ValueError as e:
            print "Configuration file does not seem to contain valid JSON data"
            print "Error was: ", e

            sys.exit(2)

        fileHandle.close()

        self.checkConfig(config)
        self.processConfig(config)

        path = "generated/" + file
        self.generateCV(path, config)

    def generateCV(self, path, config):
        """Generate the CV from the configuration"""

        # Make sure that the destination path exists
        if not os.path.exists(path):
            os.makedirs(path, 0750)

        # Get the template
        templatePath = 'templates/'
        env = Environment(loader=FileSystemLoader(templatePath))
        template = env.get_template('cv.html')

        # Generate a few variables for the template
        now = datetime.now()
        currentTime = now.strftime("%Y-%m-%d %H:%M:%S %z")
        year = now.strftime("%Y")

        navigation = self.generateNavigation(config)

        # Render the template into HTML
        html = template.render(
            name=config["name"],
            contact=config["contact"],
            sections=config["sections"],
            navigation=navigation,
            now=currentTime,
            year=year
        )

        # Copy template contents to destination
        distutils.dir_util.copy_tree(templatePath, path, update=1)

        # Figure out the filename we'll be using for the result
        fullpath = path + "/cv.html"

        # Write the result HTML
        file = codecs.open(fullpath, 'w', 'utf-8')
        file.write(html)
        file.close()

        print "Generated CV HTML to %s " % fullpath

    def checkConfig(self, config):
        """Check that the configuration looks valid"""

        error = False

        if not "name" in config:
            print 'Missing name definition, e.g. { "name": "Janne Enberg", '\
                  '... }'
            error = True

        if not "contact" in config:
            print 'Missing contact definition, e.g. { ..., '\
                  '"contact": "+1 (2) 345 678 | contact@example.com", ... }'
            error = True

        if not "sections" in config:
            print 'Missing sections definition, e.g. { ..., '\
                  '"sections": [ ... ] }'
            error = True
        else:
            for section in config["sections"]:
                # String sections need no other validation
                if isinstance(section, basestring):
                    continue

                if not "title" in section:
                    print 'Missing title from section definition, , '\
                          'e.g. { ..., "sections": [ {"title": "Section '\
                          'title", ...} ] }'
                    error = True

                if not "fields" in section and not "large" in section and \
                   not "largeList" in section:
                    print 'No fields, largeList or large definition for '\
                          'section, , '\
                          'e.g. { ..., "sections": [ {..., '\
                          '"large": "Yadi yadi yada", ...} ] }'
                    error = True

                if "fields" in section:
                    for field in section["fields"]:
                        if not isinstance(field, list) or len(field) != 2:
                            print 'Invalid field definition, '\
                                  'it should have two items, e.g. { ..., '\
                                  '"sections": [ {..., "fields": [ ["Label",'\
                                  ' "Value"], ... }, ... ] }'
                            error = True

        if error:
            print "Errors in configuration file"
            sys.exit(1)

    def processConfig(self, config):
        """Process the configuration from the readable format to a more
        useful format"""

        # Process sections
        for index, section in enumerate(config["sections"]):
            # String sections will be converted to type = heading
            if isinstance(section, basestring):
                if section == "-":
                    config["sections"][index] = {
                        "type": "page-break"
                    }

                else:
                    config["sections"][index] = {
                        "type": "heading",
                        "title": section
                    }

                continue

            # The rest are just normal sections
            section["type"] = "normal"

            # Convert ["Label", "Value"] to {"label": "Label",
            # "value": "Value"}
            if "fields" in section:
                fields = []

                for fieldColumns in section["fields"]:
                    fields.append({"label": fieldColumns[0],
                                   "value": fieldColumns[1]})

                section["fields"] = fields

            # Convert arrays in "largeList" field to <ul> -lists in "large"
            if "largeList" in section:
                section["large"] = "<ul><li>" + "</li><li>".join(
                    section["largeList"]) + "</li></ul>"

                del section["largeList"]

        heading = config["mainHeading"]

        mainHeading = {
            "type": "heading",
            "title": heading
        }

        config["sections"] = [mainHeading] + config["sections"]

    def generateNavigation(self, config):
        i = 1
        nav = {
            "headings": []
        }

        for index, section in enumerate(config["sections"]):
            # Page breaks don't need navigation
            if section["type"] == "page-break":
                continue

            name = section["title"]
            section["id"] = self.makeId(name, i)

            if section["type"] == "heading":
                nav[name] = [
                    section
                ]

                nav["headings"].append(name)

                heading = name
            else:
                nav[heading].append(section)

            i += 1

        return nav

    def makeId(self, text, index):
        # Replace characters not valid in IDs
        text = re.sub(r"[^0-9a-zA-Z\-_.:]", "-", text)

        # Text must not begin with a number
        if re.match(r"^[0-9]", text):
            text = "id-" + text

        return text

    def usage(self):
        """Print the usage and exit"""

        print "Usage: python pyhtmlcv.py cvconfig.json"
        print "Or: ./pyhtmlcv.sh cvconfig.json"

        sys.exit(1)


if __name__ == "__main__":
    instance = pyhtmlcv()
    instance.main()
