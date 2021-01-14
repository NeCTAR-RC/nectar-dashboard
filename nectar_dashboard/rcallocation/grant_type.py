GRANT_TYPES = (
    ("arc", "Australian Research Council"),
    ("nhmrc", "NHMRC"),
    ("comp", "Other Australian Federal Govt competitive grant"),
    ("govt", "Australian Federal Govt non-competitive funding"),
    ("state", "Australian State / Territory Govt funding"),
    ("industry", "Industry funding"),
    ("ext", "Other external funding"),
    ("inst", "Institutional research funding"),
    ("nz", "New Zealand research funding"),
)

GRANT_SUBTYPES = (
    # ARC grants from "An overview of ARC grant oportunities"
    # Dec 2020 edition
    ("arc-discovery", "ARC Discovery project"),
    ("arc-indigenous", "ARC Discovery Indigenous"),
    ("arc-decra", "ARC Discovery Early Career Researcher Award"),
    ("arc-future", "ARC Future Fellowship"),
    ("arc-laureate", "ARC Laureate Fellowship"),
    ("arc-itrh", "ARC Industry Transformation Research Hub"),
    ("arc-ittc", "ARC Industry Transformation Training Centre"),
    ("arc-linkage", "ARC Linkage Project"),
    ("arc-coe", "ARC Centre of Excellence"),
    ("arc-lief", "ARC Linkage Infrastructure Equipment and Facilities"),
    ("arc-sri", "ARC Special Research Initiative"),
    # NHMRC grants based on
    # https://www.nhmrc.gov.au/funding/new-grant-program/overview
    # in early 2021
    # New schemes
    ("nhmrc-investigator", "NHMRC Investigator grant"),
    ("nhmrc-synergy", "NHMRC Synergy grant"),
    ("nhmrc-ideas", "NHMRC Ideas grant"),
    ("nhmrc-strategic", "NHMRC Strategic or Leverage grant"),
    # Current / earlier schemes
    ("nhmrc-core", "NHMRC Center of Research Excellence"),
    ("nhmrc-development", "NHMRC Development grant"),
    ("nhmrc-ics", "NHMRC International Collaboration grant"),
    ("nhmrc-pbh-centre", "NHMRC Partnership for Better Health Centre"),
    ("nhmrc-pbh-project", "NHMRC Partnership for Better Health project"),
    # States and Territories
    ("act", "Australian Capital Territory Govt funding"),
    ("nsw", "New South Wales Govt funding"),
    ("nt", "Northern Territory Govt funding"),
    ("qld", "Queensland Govt funding"),
    ("sa", "South Australia Govt funding"),
    ("tas", "Tasmania Govt funding"),
    ("vic", "Victoria Govt funding"),
    ("wa", "Western Australia Govt funding"),
    # Unspecified
    ("unspecified", "unspecified"),
)
