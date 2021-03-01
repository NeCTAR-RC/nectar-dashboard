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


register = Library()


@register.filter(name='crossref_summary')
@stringfilter
def crossref_pretty_print(jsonString):
    if not jsonString:
        return "*** No JSON ***"
    try:
        data = json.loads(jsonString)
    except:
        return "*** Invalid JSON ***"
    if isinstance(data, list):
        return "*** Not a JSON object ***"
    message = data.get('message')
    if not message:
        return "*** Not a JSON Crossref response ***"
    return "Title: %s, Author(s): %s, Publication: %s, Year: %s" % (
        message['title'][0],
        format_authors(message['author']),
        message['container-title'][0],
        message['published-print']['date-parts'][0][0])


def format_authors(authors):
    return "; ".join(map(lambda author:
                         (author['family'] + "," + author['given'])
                         if author.get('given') else author['family'],
                         authors))
