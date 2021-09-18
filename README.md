JourneyLog backend module
=========================

This package provides the backend to the JourneyLog software. The frontend package can be found
[here](https://github.com/soulweaver91/journeylog-fe).

Requirements
------------

- Python 3
- A supported database, PostgreSQL or MySQL/MariaDB are safe bets
  - `pip install psycopg2==2.8.6` for PostgreSQL
  - `pip install mysqlclient` for MySQL
- `pip install -r requirements.txt`
- Apache or other WSGI compatible server software running on the server

Development
-----------

- Copy `.env.example` to `.env`, fill in accordingly
- `./manage.py migrate`
- `./manage.py runserver`
- Start coding

Deployment
----------

- Move all JourneyLog files to the destination server (checking out `master` from the repo should be fine too)
- Copy `.env.example` to `.env`, fill in accordingly
- Create a virtual env for the project, for example: `python3 -m venv journeylog-venv`
- Configure the site in your Apache installation.
  - `doc/example-apache-site.conf` is included to get you started. It contains an anonymised version of the
  configuration of a running, real-life server. Look for any paths starting with `/path/to` or anything referencing
    `example.com` and replace them with the relevant details.
  - Save the configuration to the available sites directory of your Apache installation, e.g.
    `/etc/apache2/sites-available`
  - Enable the site, e.g. `a2ensite your-conf-name`
  - Reload Apache and test the site
