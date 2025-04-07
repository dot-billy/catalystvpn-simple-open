Development Guide
===============

This guide will help you set up the development environment and contribute to the Simple Nebula API project.

Development Setup
--------------

1. Clone the repository and create a virtual environment:

   .. code-block:: bash

      git clone https://github.com/yourusername/simple-nebula.git
      cd simple-nebula
      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate

2. Install development dependencies:

   .. code-block:: bash

      pip install -r requirements-dev.txt

3. Set up pre-commit hooks (optional):

   .. code-block:: bash

      pre-commit install

Code Style
---------

The project uses several tools to maintain code quality:

* Black for code formatting
* isort for import sorting
* flake8 for linting
* mypy for type checking

Run the formatters:

.. code-block:: bash

   black .
   isort .

Run the linters:

.. code-block:: bash

   flake8
   mypy .

Running Tests
-----------

The project uses pytest for testing. Run the tests with:

.. code-block:: bash

   pytest

For coverage report:

.. code-block:: bash

   pytest --cov=. --cov-report=html

Writing Tests
-----------

Tests should be written in the ``api/tests`` directory. Follow these guidelines:

1. Use pytest fixtures for common setup
2. Test both success and failure cases
3. Use descriptive test names
4. Group related tests in test classes
5. Use parametrize for testing multiple cases

Example test:

.. code-block:: python

   import pytest
   from django.urls import reverse
   from rest_framework import status
   from rest_framework.test import APIClient

   @pytest.fixture
   def api_client():
       return APIClient()

   @pytest.fixture
   def user():
       return User.objects.create_user(
           username='testuser',
           email='test@example.com',
           password='testpass123'
       )

   def test_user_registration(api_client):
       """Test user registration endpoint."""
       url = reverse('user-list')
       data = {
           'username': 'newuser',
           'email': 'new@example.com',
           'password': 'newpass123'
       }
       response = api_client.post(url, data, format='json')
       assert response.status_code == status.HTTP_201_CREATED
       assert User.objects.filter(username='newuser').exists()

Documentation
-----------

The project uses Sphinx for documentation. Build the documentation:

.. code-block:: bash

   cd docs
   make html

The documentation will be available in ``docs/_build/html/``.

Writing Documentation
------------------

1. Add docstrings to all classes and methods
2. Use Google style docstrings
3. Include examples where appropriate
4. Keep documentation up to date with code changes

Example docstring:

.. code-block:: python

   def create_user(self, username, email, password=None):
       """Create a new user.

       Args:
           username (str): The username for the new user.
           email (str): The email address for the new user.
           password (str, optional): The password for the new user.
               If not provided, a random password will be generated.

       Returns:
           User: The newly created user.

       Raises:
           ValidationError: If the username or email is invalid.
       """
       pass

Git Workflow
----------

1. Create a new branch for your feature:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. Make your changes and commit them:

   .. code-block:: bash

      git add .
      git commit -m "Description of your changes"

3. Push your changes:

   .. code-block:: bash

      git push origin feature/your-feature-name

4. Create a pull request on GitHub

Code Review Guidelines
-------------------

1. Review the code for:
   - Functionality
   - Code style
   - Test coverage
   - Documentation
   - Security

2. Provide constructive feedback
3. Suggest improvements
4. Approve only when all issues are addressed

Release Process
-------------

1. Update version in ``simple_nebula/__init__.py``
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. Tag the release
5. Deploy to production

Example CHANGELOG.md entry:

.. code-block:: markdown

   ## [1.0.0] - 2024-02-20

   ### Added
   - Initial release
   - User authentication
   - Organization management
   - Network component management
   - Certificate management
   - API key authentication 