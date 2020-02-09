#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.
# Copyright 2019-2020 Artem Yamshanov, me [at] anticode.ninja

import datetime
import json
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

def get_name(entry):
    fields = entry.get('fields', {})
    return '{} - {}'.format(fields.get('auteur_s', ''), fields.get('personnage_s', ''))

def get_longitude(entry):
    geometry = entry.get('geometry', {})
    return geometry.get('coordinates', [0, 0])[0]

def get_latitude(entry):
    geometry = entry.get('geometry', {})
    return geometry.get('coordinates', [0, 0])[1]

def generate_kml(data):
    output = [HEAD.format(name="comic_route")]
    for point in data:
        output.append(PLACEMARK.format(
            name=escape(get_name(point)),
            description=escape(get_name(point)),
            date=datetime.datetime.now().replace(microsecond=0).isoformat(),
            longitude=get_longitude(point),
            latitude=get_latitude(point)))
    output.append(END)
    return '\n'.join(output)

def main():
    with open('comic_route.json') as input_file:
        input_data = json.load(input_file)
    kml = generate_kml(input_data)
    with open('comic_route.kml', 'w') as output_file:
        output_file.write(kml)

if __name__ == "__main__":
    main()
