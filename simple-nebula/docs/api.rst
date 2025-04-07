API Reference
=============

This section provides detailed documentation for the API endpoints.

Authentication
-------------

.. autoclass:: api.authentication.APIKeyAuthentication
   :members:
   :undoc-members:

Models
------

User
~~~~

.. autoclass:: api.models.User
   :members:
   :undoc-members:

Organization
~~~~~~~~~~~

.. autoclass:: api.models.Organization
   :members:
   :undoc-members:

Membership
~~~~~~~~~

.. autoclass:: api.models.Membership
   :members:
   :undoc-members:

CertificateAuthority
~~~~~~~~~~~~~~~~~

.. autoclass:: api.models.CertificateAuthority
   :members:
   :undoc-members:

Certificate
~~~~~~~~~~

.. autoclass:: api.models.Certificate
   :members:
   :undoc-members:

SecurityGroup
~~~~~~~~~~~

.. autoclass:: api.models.SecurityGroup
   :members:
   :undoc-members:

Node
~~~

.. autoclass:: api.models.Node
   :members:
   :undoc-members:

Lighthouse
~~~~~~~~~

.. autoclass:: api.models.Lighthouse
   :members:
   :undoc-members:

APIKey
~~~~~

.. autoclass:: api.models.APIKey
   :members:
   :undoc-members:

Serializers
----------

UserSerializer
~~~~~~~~~~~~

.. autoclass:: api.serializers.UserSerializer
   :members:
   :undoc-members:

OrganizationSerializer
~~~~~~~~~~~~~~~~~~~

.. autoclass:: api.serializers.OrganizationSerializer
   :members:
   :undoc-members:

MembershipSerializer
~~~~~~~~~~~~~~~~~

.. autoclass:: api.serializers.MembershipSerializer
   :members:
   :undoc-members:

CertificateAuthoritySerializer
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: api.serializers.CertificateAuthoritySerializer
   :members:
   :undoc-members:

CertificateSerializer
~~~~~~~~~~~~~~~~~~

.. autoclass:: api.serializers.CertificateSerializer
   :members:
   :undoc-members:

SecurityGroupSerializer
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: api.serializers.SecurityGroupSerializer
   :members:
   :undoc-members:

NodeSerializer
~~~~~~~~~~~

.. autoclass:: api.serializers.NodeSerializer
   :members:
   :undoc-members:

LighthouseSerializer
~~~~~~~~~~~~~~~~~

.. autoclass:: api.serializers.LighthouseSerializer
   :members:
   :undoc-members:

APIKeySerializer
~~~~~~~~~~~~~

.. autoclass:: api.serializers.APIKeySerializer
   :members:
   :undoc-members:

Views
-----

UserViewSet
~~~~~~~~~

.. autoclass:: api.views.auth.UserViewSet
   :members:
   :undoc-members:

OrganizationViewSet
~~~~~~~~~~~~~~~~

.. autoclass:: api.views.auth.OrganizationViewSet
   :members:
   :undoc-members:

MembershipViewSet
~~~~~~~~~~~~~~

.. autoclass:: api.views.auth.MembershipViewSet
   :members:
   :undoc-members:

CertificateAuthorityViewSet
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: api.views.certificates.CertificateAuthorityViewSet
   :members:
   :undoc-members:

CertificateViewSet
~~~~~~~~~~~~~~~

.. autoclass:: api.views.certificates.CertificateViewSet
   :members:
   :undoc-members:

SecurityGroupViewSet
~~~~~~~~~~~~~~~~~

.. autoclass:: api.views.network.SecurityGroupViewSet
   :members:
   :undoc-members:

NodeViewSet
~~~~~~~~~

.. autoclass:: api.views.network.NodeViewSet
   :members:
   :undoc-members:

LighthouseViewSet
~~~~~~~~~~~~~~

.. autoclass:: api.views.network.LighthouseViewSet
   :members:
   :undoc-members:

APIKeyViewSet
~~~~~~~~~~~

.. autoclass:: api.views.api_key.APIKeyViewSet
   :members:
   :undoc-members: 