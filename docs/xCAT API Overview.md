# xCAT API Overview

This page provides an overview of the xCAT API.

- API versioning
- API terminology
- API bulk operation
- API query parameter
- API response

The REST API (v2) is the fundamental component of xCAT, all operations and interactions between components, and CLIs are REST API calls. Consequently, everything in the xCAT cluster is treated as an API resource and has a corresponding object in the API.


## API versioning
Before xCAT 2.15, the existing xCAT REST API (v1) is just implemented as a front end (translation layer) to xcatd.
And now it is dropped after the new REST API (v2) released.


## API terminology

Most xCAT API resource types are "objects" - they represent a concrete instance of a concept on the cluster, like a node or subnet. All objects will have a unique name to allow idempotent creation and retrieval.

xCAT generally leverages standard RESTful terminology to describe the API concepts:

- A resource type is the name used in the URL (nodes, subnets, services).
- A list of instances of a resource type is known as a collection.
- A single instance of the resource type is called a resource.

API ``namespace`` make it easier to extend the xCAT API. The API namespace is specified in a REST path (For example, `/api/v2/<namespace>/<resource>`).

Currently, there are several API namespace in use:

- **globalconf**: Global configuration
- **auth**: Authentication, authorization and security stuffs
- **inventory**: Networking, Distro, OS image related objects
- **node**: Node inventory, Node group, etc.
- **service**: Services related operations
- **task**: Async administrative tasks (TBD).
- **table**: Internal objects on DB tables operation (Deprecated)

## API bulk operation
xCAT can support bulk operations on multiple objects for some of the resource kind. This is implemented via a POST operation on a special REST path.

- Search by complex conditions: `POST /api/v2/<namespace>/<kind>/_msearch`
- Delete by complex conditions: `POST /api/v2/<namespace>/<kind>/_mdelete`
- Update by complex conditions: `POST /api/v2/<namespace>/<kind>/_mupdate`
- General bulk operations: `POST /api/v2/<namespace>/<kind>/_bulk`


## API query parameter
xCAT REST API supports several query parameters in the resource URI.


	GET <path>?limit=10: Reduce the number of results returned to the client (for Pagination)
	GET <path>?offset=10: Send sets of information to the client (for Pagination)


## API response
For sucessful request, the xCAT API will response with the JSON format of the object.

If error is found, the JSON object should be as below:

		{
		   error:[
		       msg1,
		       msg2,
		       ...
		   ],
		   errorcode:error_number
		}


The HTTP status code as below:

        200 OK
        201 CREATED - [POST/PUT/PATCH]
        204 NO CONTENT - [DELETE]
        400 BAD REQUEST - [POST/PUT/PATCH]
        401 Unauthorized
        403 Forbidden
        404 NOT FOUND - [*]
        405 Method Not Allowed
        500 INTERNAL SERVER ERROR

