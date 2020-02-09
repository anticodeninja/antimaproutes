#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Copyright 2019-2020 Artem Yamshanov, me [at] anticode.ninja

import argparse
import datetime
import json
import os

from xml.sax.saxutils import escape

HEAD = """\
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Document>
  <Style id="placemark-red">
    <IconStyle>
      <Icon>
        <href>http://maps.me/placemarks/placemark-red.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <name>{name}</name>
  <visibility>1</visibility>"""

PLACEMARK = """\
  <Placemark>
    <name>{name}</name>
    <description>{description}</description>
    <TimeStamp><when>{date}</when></TimeStamp>
    <styleUrl>#placemark-red</styleUrl>
    <Point><coordinates>{longitude},{latitude}</coordinates></Point>
  </Placemark>"""

END = """\
</Document>
</kml>"""

class Point:

    def __init__(self, name, description, longitude, latitude):
        self.name = name
        self.description = description
        self.longitude = longitude
        self.latitude = latitude

class ComicSource:

    def __init__(self, filename):
        with open(filename, 'rb') as input_file:
            self.input_data = json.load(input_file)

    def title(self):
        return "comic_route"

    def enumerate(self):
        for point in self.input_data:
            yield Point(ComicSource.get_name(point),
                        ComicSource.get_name(point),
                        ComicSource.get_longitude(point),
                        ComicSource.get_latitude(point))

    @staticmethod
    def get_name(entry):
        fields = entry.get('fields', {})
        return '{} - {}'.format(fields.get('auteur_s', ''), fields.get('personnage_s', ''))

    @staticmethod
    def get_longitude(entry):
        geometry = entry.get('geometry', {})
        return geometry.get('coordinates', [0, 0])[0]

    @staticmethod
    def get_latitude(entry):
        geometry = entry.get('geometry', {})
        return geometry.get('coordinates', [0, 0])[1]


class GoogleSource:

    def __init__(self, filename):
        self.input_data = []
        with open(filename, 'rb') as input_file:
            for line in input_file.read().decode('utf-8').splitlines():
                outer = json.loads(line[:-6])
                self.input_data.append(json.loads(outer['d'][4:]))

    def title(self):
        return GoogleSource.traverse(self.input_data, [0, 32, 1])

    def enumerate(self):
        for response in self.input_data:
            for point in GoogleSource.traverse(response, [0, 1]):
                yield Point(GoogleSource.traverse(point, [14, 11]),
                            GoogleSource.traverse(point, [14, 25, 15, 0, 2]) or '',
                            GoogleSource.traverse(point, [14, 9, 2]),
                            GoogleSource.traverse(point, [14, 9, 3]))

    @staticmethod
    def traverse(data, path):
        try:
            el = data
            for i in path:
                el = el[i]
            return el
        except:
            return None


def generate_kml(filename, source):
    output = [HEAD.format(name=source.title())]
    for point in source.enumerate():
        output.append(PLACEMARK.format(
            name=escape(point.name),
            description=escape(point.description),
            date=datetime.datetime.now().replace(microsecond=0).isoformat(),
            longitude=point.longitude,
            latitude=point.latitude))
    output.append(END)

    with open(filename, 'wb') as output_file:
        output_file.write('\n'.join(output).encode('utf-8'))
    print("{} points written to {}".format(len(output) - 2, filename))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    if args.filename == 'comic_route.json':
        source = ComicSource(args.filename)
    elif args.filename.endswith('.google'):
        source = GoogleSource(args.filename)

    generate_kml(os.path.splitext(args.filename)[0] + '.kml', source)

if __name__ == "__main__":
    main()
