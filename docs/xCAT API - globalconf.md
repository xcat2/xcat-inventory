# xCAT API - globalconf

This page provides information of ``globalconf`` namespace in the xCAT API.

- site Resource
- secret Resource


The below URI list which can be used to create, query, change global configuration.

## site Resource

### Retrieve site collection
Query all site contexts defined xCAT, now only support one named `default`

#### HTTP Request
`GET /globalconf/sites`

#### Path Parameters
N/A

#### Query Parameters
N/A

#### Response
| Code   |Description      |
|-------------|-----------------|
| 200 |  OK |


### Create a site resource
Not supported yet, as `default` is created automatically.

#### HTTP Request
`POST /globalconf/sites`

#### Path Parameters
N/A

#### Body Parameters
A JSON object with full site attributes

#### Response
| Code   |Description      |
|-------------|-----------------|
| 201 |  OK |


### Get a specified site resource
Query site attributes filtered by query parameters

#### HTTP Request
`GET /globalconf/sites/<name>`

#### Path Parameters
| Parameter   |Description      |
|-------------|-----------------|
| name |  name of the context |

#### Query Parameters
| Parameter   |Description      | Format |
|-------------|-----------------|--------|
| attr |  name of the attribute | multiple valuses

#### Response
| Code   |Description      |
|-------------|-----------------|
| 200 |  OK |

