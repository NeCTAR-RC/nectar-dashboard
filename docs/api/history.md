# Allocation API version history

## 1.0
Initial release


## 1.1
_Released 2023-12-07_
* Added new API for [Organisations](organisations.md) at /organisations
* Removed /institutions API, this has been replaced with `Organisations`
* Added `supported_organisations` field to `Allocation` object
* Added `primary_organisation` to `ChiefInvestigator` object
* Removed `institution` field from `ChiefInvestigator` object
