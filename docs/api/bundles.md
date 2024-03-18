# Bundles API

A resource bundle is a collection of resource quotas. An `Allocation` can
have a bundle which means it receives all the resource quotas of a bundle.

Alternatively an allocation can have no bundle and specify a quota for each
resource seperatly. It can also have a mix of the 2 with specific quota
overriding any resource specified in a bundle.

## Attributes
* name - name of bundle
* description - Longer description of bundle
* order - In what order should the bundle appear in a list of form selection
* zone - The `Zone` to which quota applies to all resources in a bundle
* su_per_year - The amount of SU budget granted to allocation. Allocations less
                than a year will receive a propotional amount


### POST /bundles/
Create a bundle
```
 {
     "name": "Gold",
     "description": "Our best offering giving you access to lots of resources",
     "order": 1,
     "zone": "my-zone",
     "su_per_year": 200,
  }
```

### GET /bundles/
List all bundles

### GET /bundles/\<id>\/
Get details of an bundle
```
 {
     "id": 1,
     "name": "Gold",
     "description": "Our best offering giving you access to lots of resources",
     "order": 1,
     "zone": "my-zone",
     "su_per_year": 200,
     "quotas": [
       {"zone": "my-zone",
        "resource": "network.floatingip",
        "quota": 8},
       {"zone": "my-zone",
        "resource": "compute.instances",
        "quota": 40
       }
     ]
  }
```
