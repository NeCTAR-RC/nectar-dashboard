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

PEER_REVIEWED_JOURNAL_ARTICLE = 'AJ'
OTHER_PEER_REVIEWED_PAPER = 'AP'
NON_PEER_REVIEWED_PAPER = 'AN'
BOOK = 'B'
MEDIA_PUBLICATION = 'M'
DATASET = 'D'
SOFTWARE = 'S'
PATENT = 'P'
OTHER = 'O'
UNSPECIFIED = 'U'

OUTPUT_TYPE_CHOICE = (
    (PEER_REVIEWED_JOURNAL_ARTICLE, 'Peer reviewed journal article'),
    (OTHER_PEER_REVIEWED_PAPER, 'Other peer reviewed paper'),
    (NON_PEER_REVIEWED_PAPER, 'Non-peer reviewed paper'),
    (BOOK, 'Book or book chapter'),
    (MEDIA_PUBLICATION, 'Media publication'),  # includes new media
    (DATASET, 'Dataset'),
    (SOFTWARE, 'Software'),
    (PATENT, 'Patent'),
    (OTHER, 'Other'),
    (UNSPECIFIED, 'Unspecified'),  # for legacy cases only
)
OUTPUT_TYPE_MAP = dict(OUTPUT_TYPE_CHOICE)
