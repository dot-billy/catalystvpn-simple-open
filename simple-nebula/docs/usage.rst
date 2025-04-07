Usage Guide
===========

This guide will help you understand how to use the Simple Nebula API.

Authentication
-------------

The API supports two authentication methods:

JWT Authentication
~~~~~~~~~~~~~~~~

1. Obtain a token by sending a POST request to ``/api/token/``:

   .. code-block:: bash

      curl -X POST http://localhost:8000/api/token/ \
           -H "Content-Type: application/json" \
           -d '{"username": "your_username", "password": "your_password"}'

2. Include the token in subsequent requests:

   .. code-block:: bash

      curl http://localhost:8000/api/users/me/ \
           -H "Authorization: Bearer your_token_here"

API Key Authentication
~~~~~~~~~~~~~~~~~~~~

1. Generate an API key through the API:

   .. code-block:: bash

      curl -X POST http://localhost:8000/api/api-keys/ \
           -H "Authorization: Bearer your_token_here" \
           -H "Content-Type: application/json" \
           -d '{"name": "My API Key", "entity_type": "node"}'

2. Include the API key in requests:

   .. code-block:: bash

      curl http://localhost:8000/api/nodes/ \
           -H "Authorization: Api-Key your_api_key_here"

Organizations
------------

Create an Organization
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   curl -X POST http://localhost:8000/api/organizations/ \
        -H "Authorization: Bearer your_token_here" \
        -H "Content-Type: application/json" \
        -d '{"name": "My Organization", "description": "My organization description"}'

List Organizations
~~~~~~~~~~~~~~~~

.. code-block:: bash

   curl http://localhost:8000/api/organizations/ \
        -H "Authorization: Bearer your_token_here"

Network Components
----------------

Create a Node
~~~~~~~~~~~

.. code-block:: bash

   curl -X POST http://localhost:8000/api/organizations/{org_id}/nodes/ \
        -H "Authorization: Bearer your_token_here" \
        -H "Content-Type: application/json" \
        -d '{
          "name": "My Node",
          "description": "My node description",
          "public_key": "node_public_key",
          "endpoint": "node_endpoint"
        }'

Create a Lighthouse
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   curl -X POST http://localhost:8000/api/organizations/{org_id}/lighthouses/ \
        -H "Authorization: Bearer your_token_here" \
        -H "Content-Type: application/json" \
        -d '{
          "name": "My Lighthouse",
          "description": "My lighthouse description",
          "public_key": "lighthouse_public_key",
          "endpoint": "lighthouse_endpoint"
        }'

Security Groups
~~~~~~~~~~~~~

Create a Security Group
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   curl -X POST http://localhost:8000/api/organizations/{org_id}/security-groups/ \
        -H "Authorization: Bearer your_token_here" \
        -H "Content-Type: application/json" \
        -d '{
          "name": "My Security Group",
          "description": "My security group description",
          "rules": [
            {
              "port": "any",
              "protocol": "any",
              "hosts": ["*"]
            }
          ]
        }'

Certificates
----------

Generate a Certificate
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   curl -X POST http://localhost:8000/api/organizations/{org_id}/certificates/ \
        -H "Authorization: Bearer your_token_here" \
        -H "Content-Type: application/json" \
        -d '{
          "name": "My Certificate",
          "type": "node",
          "public_key": "certificate_public_key"
        }'

API Documentation
---------------

The API documentation is available at:

* Swagger UI: http://localhost:8000/api/docs/
* ReDoc: http://localhost:8000/api/redoc/
* OpenAPI Schema: http://localhost:8000/api/schema/

These interactive documentation pages provide detailed information about all available endpoints, request/response formats, and authentication methods. 