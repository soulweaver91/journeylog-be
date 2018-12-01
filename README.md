JourneyLog backend module
=========================

This package provides the backend to the JourneyLog software. The frontend package can be found
[here](https://github.com/soulweaver91/journeylog-fe).

Requirements
------------

- Python 3
- A supported database, PostgreSQL or MySQL/MariaDB are safe bets
- `pip install -r requirements.txt`
- Apache, nginx, etc. running on the same server (for image hosting etc.)

Development
-----------

- Copy `.env.example` to `.env`, fill in accordingly
- `./manage.py migrate`
- `./manage.py runserver`
- Start coding

Deployment
----------

TODO
