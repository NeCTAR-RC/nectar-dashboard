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

from nectar_dashboard.rcallocation import models
from nectar_dashboard.rcallocation import output_type_choices
from nectar_dashboard.rcallocation.templatetags import publication_extras
from nectar_dashboard.rcallocation.tests import base


class PublicationExtrasTestCase(base.BaseTestCase):
    def test_crossref_summary(self):
        self.assertEqual(
            "*** No JSON ***", publication_extras.crossref_summary("")
        )
        self.assertEqual(
            "*** Invalid JSON ***",
            publication_extras.crossref_summary("Jason"),
        )
        self.assertEqual(
            "*** Not a JSON object ***",
            publication_extras.crossref_summary('["Jason"]'),
        )
        self.assertEqual(
            "*** Not a JSON Crossref response ***",
            publication_extras.crossref_summary('{"name": "Jason"}'),
        )

        self.assertEqual(
            "<i>Title</i>: Not recorded, "
            "<i>Author(s)</i>: Not recorded, "
            "<i>Publication</i>: Not recorded, "
            "<i>Year</i>: Not recorded",
            publication_extras.crossref_summary('{"message": {"abc": 123}}'),
        )

        self.assertEqual(
            "<i>Title</i>: one, "
            "<i>Author(s)</i>: Not recorded, "
            "<i>Publication</i>: Not recorded, "
            "<i>Year</i>: Not recorded",
            publication_extras.crossref_summary(
                '{"message": {"title": ["one", "two"]}}'
            ),
        )
        # Prevent injection via the title
        self.assertEqual(
            "<i>Title</i>: &lt;i&gt;one&lt;/i&gt;, "
            "<i>Author(s)</i>: Not recorded, "
            "<i>Publication</i>: Not recorded, "
            "<i>Year</i>: Not recorded",
            publication_extras.crossref_summary(
                '{"message": {"title": ["<i>one</i>", "two"]}}'
            ),
        )

        self.assertEqual(
            "<i>Title</i>: Not recorded, "
            "<i>Author(s)</i>: Nurke,Fred, "
            "<i>Publication</i>: Not recorded, "
            "<i>Year</i>: Not recorded",
            publication_extras.crossref_summary(
                '{"message": {"author": [{"family": "Nurke",'
                '                         "given": "Fred"}]}}'
            ),
        )
        self.assertEqual(
            "<i>Title</i>: Not recorded, "
            "<i>Author(s)</i>: Nurke,Fred; Spriggs,Jim, "
            "<i>Publication</i>: Not recorded, "
            "<i>Year</i>: Not recorded",
            publication_extras.crossref_summary(
                '{"message": {"author": [{"family": "Nurke",'
                '                         "given": "Fred"},'
                '                        {"family": "Spriggs",'
                '                         "given": "Jim"}]}}'
            ),
        )
        self.assertEqual(
            "<i>Title</i>: Not recorded, "
            "<i>Author(s)</i>: Moriarty; Eccles, "
            "<i>Publication</i>: Not recorded, "
            "<i>Year</i>: Not recorded",
            publication_extras.crossref_summary(
                '{"message": '
                ' {"author": [{"family": "Moriarty"},'
                '             {"family": "Eccles"}]}}'
            ),
        )
        self.assertEqual(
            "<i>Title</i>: Not recorded, "
            "<i>Author(s)</i>: Moriarty; Eccles, "
            "<i>Publication</i>: Not recorded, "
            "<i>Year</i>: Not recorded",
            publication_extras.crossref_summary(
                '{"message": '
                ' {"author": [{"name": "Moriarty"},'
                '             {"name": "Eccles"}]}}'
            ),
        )
        self.assertEqual(
            "<i>Title</i>: Not recorded, "
            "<i>Author(s)</i>: Moriarty; Eccles, "
            "<i>Publication</i>: Not recorded, "
            "<i>Year</i>: Not recorded",
            publication_extras.crossref_summary(
                '{"message": '
                ' {"author": [{"name": "Moriarty"},'
                '             {"name": "Eccles"}]}}'
            ),
        )
        self.assertEqual(
            "<i>Title</i>: Not recorded, "
            "<i>Author(s)</i>: one; two; three; four; five, "
            "<i>Publication</i>: Not recorded, "
            "<i>Year</i>: Not recorded",
            publication_extras.crossref_summary(
                '{"message": '
                ' {"author": [{"name": "one"},'
                '             {"name": "two"},'
                '             {"name": "three"},'
                '             {"name": "four"},'
                '             {"name": "five"}]}}'
            ),
        )
        self.assertEqual(
            "<i>Title</i>: Not recorded, "
            "<i>Author(s)</i>: one; two; three; "
            "four; five ..., "
            "<i>Publication</i>: Not recorded, "
            "<i>Year</i>: Not recorded",
            publication_extras.crossref_summary(
                '{"message": '
                ' {"author": [{"name": "one"},'
                '             {"name": "two"},'
                '             {"name": "three"},'
                '             {"name": "four"},'
                '             {"name": "five"},'
                '             {"name": "six"}]}}'
            ),
        )
        # Prevent injection via the authors
        self.assertEqual(
            "<i>Title</i>: Not recorded, "
            "<i>Author(s)</i>: &lt;tag&gt;&amp;, "
            "<i>Publication</i>: Not recorded, "
            "<i>Year</i>: Not recorded",
            publication_extras.crossref_summary(
                '{"message": ' ' {"author": [{"family": "<tag>&"}]}}'
            ),
        )

        self.assertEqual(
            "<i>Title</i>: Not recorded, "
            "<i>Author(s)</i>: Not recorded, "
            "<i>Publication</i>: Some Journal, "
            "<i>Year</i>: Not recorded",
            publication_extras.crossref_summary(
                '{"message": ' '  {"container-title": ["Some Journal"]}}'
            ),
        )
        # Prevent injection via the title
        self.assertEqual(
            "<i>Title</i>: Not recorded, "
            "<i>Author(s)</i>: Not recorded, "
            "<i>Publication</i>: &lt;beep&gt;, "
            "<i>Year</i>: Not recorded",
            publication_extras.crossref_summary(
                '{"message": ' '  {"container-title": ["<beep>"]}}'
            ),
        )

        self.assertEqual(
            "<i>Title</i>: Not recorded, "
            "<i>Author(s)</i>: Not recorded, "
            "<i>Publication</i>: Not recorded, "
            "<i>Year</i>: 2021",
            publication_extras.crossref_summary(
                '{"message": '
                '  {"published-online": '
                '    {"date-parts": [[2021, 4, 1]]}}}'
            ),
        )
        self.assertEqual(
            "<i>Title</i>: Not recorded, "
            "<i>Author(s)</i>: Not recorded, "
            "<i>Publication</i>: Not recorded, "
            "<i>Year</i>: 2021",
            publication_extras.crossref_summary(
                '{"message": '
                '  {"published-print": '
                '    {"date-parts": [[2021, 4, 1]]}}}'
            ),
        )
        # Prevent injection via the year
        self.assertEqual(
            "<i>Title</i>: Not recorded, "
            "<i>Author(s)</i>: Not recorded, "
            "<i>Publication</i>: Not recorded, "
            "<i>Year</i>: &lt;1066&gt;",
            publication_extras.crossref_summary(
                '{"message": '
                '  {"published-online": '
                '    {"date-parts": [["<1066>", 4, 1]]}}}'
            ),
        )

    def test_pub_summary(self):
        pub = models.Publication(
            output_type=output_type_choices.OTHER,
            doi='10.004/1234',
            crossref_metadata='{"message": {"a": "b"}}',
        )
        self.assertEqual(
            "<i>Type</i>: Other, "
            "<i>DOI</i>: 10.004/1234 (validated), "
            "<i>Title</i>: Not recorded, "
            "<i>Author(s)</i>: Not recorded, "
            "<i>Publication</i>: Not recorded, "
            "<i>Year</i>: Not recorded",
            publication_extras.pub_summary(pub),
        )

        pub = models.Publication(
            output_type=output_type_choices.OTHER,
            doi='10.004/1234',
            publication='cite this',
        )
        self.assertEqual(
            "<i>Type</i>: Other, "
            "<i>DOI</i>: 10.004/1234 (not validated), "
            "<i>Citation reference</i>: cite this",
            publication_extras.pub_summary(pub),
        )

        pub = models.Publication(
            output_type=output_type_choices.OTHER,
            doi='<10.004/1234>',
            publication='<cite this>',
        )
        self.assertEqual(
            "<i>Type</i>: Other, "
            "<i>DOI</i>: &lt;10.004/1234&gt; (not validated), "
            "<i>Citation reference</i>: &lt;cite this&gt;",
            publication_extras.pub_summary(pub),
        )
