# Organisations API

Organisations are used by `Allocations` and `ChiefInvestigators`, when linking
organisations to these objects you can use `ror_id`, `short_name` or
`full_name` as the reference.


### POST /organisations/
Propose an institution
```
 {
     "full_name": "Australian Research Data Commons",
     "short_name": "ARDC",
     "url": "https://ardc.edu.au",
     "country": "AU",
  }
```

### GET /organisations/
List all organisations

### GET /organisations/\<id>\/
Get details of an organisation
```
{
     "id": 248640,
     "precedes": [],
     "ror_id": "https://ror.org/038sjwq14",
     "full_name": "Australian Research Data Commons",
     "short_name": "ARDC",
     "url": "https://ardc.edu.au",
     "country": "AU",
     "enabled": true,
     "proposed_by": "",
     "parent": null,
     "vetted_by": null
 }
```
NOTE: proposed_by and vetted_by are only visible with admin permissions

### POST /organisations/\<id\>/approve/
Approve a proposed organisation

NOTE: Required admin permissions

### POST /organisations/\<id\>/decline/
Decline a proposed organisation

NOTE: Required admin permissions
