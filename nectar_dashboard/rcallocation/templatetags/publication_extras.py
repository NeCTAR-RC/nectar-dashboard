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

from nectar_dashboard.rcallocation import output_type_choices

register = Library()


@register.filter()
def pub_summary(publication):
    res = "Type: %s" % output_type_choices.description(
        publication.output_type)
    if publication.doi:
        res = res + ", DOI: %s (%s)" % (
            publication.doi,
            "validated" if publication.crossref_metadata else "not validated")
    if publication.crossref_metadata:
        res = res + ", " + crossref_summary(publication.crossref_metadata)
    else:
        res = res + ", Other details: %s" % publication.publication
    return res


@register.filter()
@stringfilter
def output_type_descr(output_type):
    return output_type_choices.description(output_type)


@register.filter()
@stringfilter
def crossref_summary(jsonString):
    if not jsonString:
        return "*** No JSON ***"
    try:
        data = json.loads(jsonString)
    except json.JSONDecodeError:
        return "*** Invalid JSON ***"
    if isinstance(data, list):
        return "*** Not a JSON object ***"
    msg = data.get('message')
    if not msg:
        return "*** Not a JSON Crossref response ***"
    return "Title: %s, Author(s): %s, Publication: %s, Year: %s" % (
        format_title(msg), format_authors(msg),
        format_publication(msg), format_pub_date(msg))


def format_title(msg):
    return msg.get('title') or 'Not recorded'


def format_publication(msg):
    return msg.get('container-title') or 'Not recorded'


def format_pub_date(msg):
    pub_date = msg.get('published-print') or msg.get('published-online')
    return pub_date['date-parts'][0][0] if pub_date else 'Not recorded'


def format_authors(msg):
    authors = msg.get('author')
    return "; ".join(map(lambda author:
                         (author['family'] + "," + author['given'])
                         if author.get('given') else author['family'],
                         authors)) if authors else 'Not recorded'
