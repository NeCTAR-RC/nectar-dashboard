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
    (MEDIA_PUBLICATION, 'Media publication'),   # includes new media
    (DATASET, 'Dataset'),
    (SOFTWARE, 'Software'),
    (PATENT, 'Patent'),
    (OTHER, 'Other'),
    (UNSPECIFIED, 'Unspecified'),               # for legacy cases only
)
