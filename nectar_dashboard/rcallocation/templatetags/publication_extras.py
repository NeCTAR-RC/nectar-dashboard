# Copyright 2021 Australian Research Data Commons
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json

from django.template.defaultfilters import stringfilter
from django.template import Library
from django.utils.html import escape

register = Library()


@register.filter()
def pub_summary(publication):
    res = f"<i>Type</i>: {publication.get_output_type_display()}"
    if publication.doi:
        res = res + ", <i>DOI</i>: {} ({})".format(
            escape(publication.doi),
            "validated" if publication.crossref_metadata else "not validated",
        )
    if publication.crossref_metadata:
        res = res + ", " + crossref_summary(publication.crossref_metadata)
    else:
        res = (
            res
            + f", <i>Citation reference</i>: {escape(publication.publication)}"
        )
    return res


@register.filter()
@stringfilter
def crossref_summary(jsonString):
    if not jsonString:
        return "*** No JSON ***"
    try:
        data = json.loads(jsonString)
    except json.JSONDecodeError:
        return "*** Invalid JSON ***"
    if not isinstance(data, dict):
        return "*** Not a JSON object ***"
    msg = data.get('message')
    if not msg:
        return "*** Not a JSON Crossref response ***"
    return (
        f"<i>Title</i>: {format_title(msg)}, "
        f"<i>Author(s)</i>: {format_authors(msg)}, "
        f"<i>Publication</i>: {format_publication(msg)}, "
        f"<i>Year</i>: {format_pub_date(msg)}"
    )


def format_title(msg):
    if msg.get('title'):
        return escape(msg.get('title')[0])
    else:
        return 'Not recorded'


def format_publication(msg):
    if msg.get('container-title'):
        return escape(msg.get('container-title')[0])
    else:
        return 'Not recorded'


def format_pub_date(msg):
    pub_date = msg.get('published-print') or msg.get('published-online')
    return escape(pub_date['date-parts'][0][0]) if pub_date else 'Not recorded'


def format_author_name(author):
    if 'family' in author:
        if 'given' in author:
            return author['family'] + "," + author['given']
        else:
            return author['family']
    elif 'given' in author:
        return author['given']
    elif 'name' in author:
        return author['name']
    else:
        return 'no name'


def format_authors(msg):
    # Limit to the first 5 authors with elipsis
    authors = msg.get('author')
    if authors:
        str = "; ".join(map(format_author_name, authors[:5]))
        if len(authors) > 5:
            str = str + " ..."
        return escape(str)
    else:
        return 'Not recorded'
