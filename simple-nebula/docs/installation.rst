Installation
============

This guide will help you set up the Simple Nebula API for development or production use.

Prerequisites
------------

* Python 3.8 or higher
* pip (Python package manager)
* Virtual environment (recommended)

Development Installation
-----------------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/yourusername/simple-nebula.git
      cd simple-nebula

2. Create and activate a virtual environment:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:

   .. code-block:: bash

      pip install -r requirements.txt
      pip install -r requirements-dev.txt  # For development dependencies

4. Create a `.env` file in the project root:

   .. code-block:: bash

      cp .env.example .env
      # Edit .env with your settings

5. Run migrations:

   .. code-block:: bash

      python manage.py migrate

6. Create a superuser (optional):

   .. code-block:: bash

      python manage.py createsuperuser

7. Run the development server:

   .. code-block:: bash

      python manage.py runserver

The API will be available at http://localhost:8000/api/

Production Installation
----------------------

For production deployment, follow these additional steps:

1. Set up a production-grade database (PostgreSQL recommended)
2. Configure proper CORS settings
3. Set up a production-grade server (e.g., Gunicorn)
4. Configure proper static file serving
5. Set up proper security settings

Environment Variables
-------------------

The following environment variables can be configured:

* ``DJANGO_DEBUG``: Set to False in production
* ``DJANGO_SECRET_KEY``: Your Django secret key
* ``DJANGO_ALLOWED_HOSTS``: Comma-separated list of allowed hosts
* ``CORS_ALLOWED_ORIGINS``: Comma-separated list of allowed CORS origins
* ``DATABASE_URL``: Database connection URL
* ``REDIS_URL``: Redis connection URL (optional, for caching)

Example `.env` file:

.. code-block:: text

   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=your-secret-key-here
   DJANGO_ALLOWED_HOSTS=example.com,www.example.com
   CORS_ALLOWED_ORIGINS=https://example.com
   DATABASE_URL=postgres://user:password@localhost:5432/dbname
   REDIS_URL=redis://localhost:6379/0 