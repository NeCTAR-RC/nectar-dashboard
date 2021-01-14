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
    ("arc-itrp", "ARC Industry Transformation Research Program"),
    ("arc-linkage", "ARC Linkage Project"),
    ("arc-coe", "ARC Centre of Excellence"),
    ("arc-lief", "ARC Linkage Infrastructure Equipment and Facilities"),
    ("arc-sri", "ARC Special Research Initiative"),
    # Other schemes from NCRIS reporting form
    ("arc-llasp", "ARC Linkage Learned Academies Special Project"),
    ("arc-other", "Other ARC grant"),
    # NHMRC grants based on
    # https://www.nhmrc.gov.au/funding/new-grant-program/overview
    # in early 2021
    # New schemes
    ("nhmrc-investigator", "NHMRC Investigator grant"),
    ("nhmrc-synergy", "NHMRC Synergy grant"),
    ("nhmrc-ideas", "NHMRC Ideas grant"),
    ("nhmrc-strategic", "NHMRC Strategic or Leverage grant"),
    # Current / earlier schemes from NCRIS reporting form
    ("nhmrc-program", "NHMRC Program grant"),
    ("nhmrc-project", "NHMRC Project grant"),
    ("nhmrc-fas", "NHMRC Fellowship or Scholarship (various)"),
    ("nhmrc-core", "NHMRC Center of Research Excellence"),
    ("nhmrc-development", "NHMRC Development grant"),
    ("nhmrc-equipment", "NHMRC Equipment grant"),
    ("nhmrc-ctcs", "NHMRC Clinical Trial and Cohort Studies grant"),
    ("nhmrc-ics", "NHMRC International Collaborations (various)"),
    ("nhmrc-pc", "NHMRC Partnership Centre"),
    ("nhmrc-pp", "NHMRC Partnership project"),
    ("nhmrc-tcr", "NHMRC Targeted Calls for Research"),
    ("nhmrc-iriiss",
     "NHMRC Independent Research Institute Infrastructure Support Scheme"),
    ("nhmrc-bdri", "NHMRC Boosting Dementia Research Initiatives (various)"),
    ("nhmrc-other", "Other NHMRC scheme"),
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
