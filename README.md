﻿# AsylumConnect [![Circle CI](https://circleci.com/gh/hack4impact/flask-base.svg?style=svg)](https://circleci.com/gh/hack4impact/flask-base) [![Stories in Ready](https://badge.waffle.io/hack4impact/flask-base.png?label=ready&title=Ready)](https://waffle.io/hack4impact/flask-base)

## Team Members

- Hunter Lightman
- Yoni Nachmany
- Hana Pearlman
- Veronica Wharton

## Synopsis

AsylumConnect’s current resource verification model is a bottleneck, as volunteers must search for and independently verify resources for each city that the organization expands into. In addition, volunteers are not (all) members of their target community, and therefore not the best-equipped to verify resource information. By allowing community members to tag, verify, endorse, and report resources, AsylumConnect will leverage its niche and highly marginalized community while also keeping members as safe as possible.

## What's included?

* Blueprints
* User and permissions management
* Flask-SQLAlchemy for databases
* Flask-WTF for forms
* Flask-Assets for asset management and SCSS compilation
* Flask-Mail for sending emails
* Automatic SSL + gzip compression

## Setting up

1. Clone the repo

    ```
    $ git clone https://github.com/hack4impact/asylum-connect-catalog.git
    $ cd asylum-connect-catalog
    ```

2. Initialize a virtualenv

    ```
    $ pip install virtualenv
    $ virtualenv env
    $ source env/bin/activate
    ```

3. (If you're on a mac) Make sure Xcode tools are installed
    ```
    $ xcode-select --install
    ```

4. Install the dependencies

    ```
    $ pip install -r requirements/common.txt
    $ pip install -r requirements/dev.txt
    ```

5. Create the database

    ```
    $ python manage.py recreate_db
    ```

6. Other setup (e.g. creating roles in database)

    ```
    $ python manage.py setup_dev
    ```

6. [Optional] Add Seattle data and fake data to the database.

    ```
    $ python manage.py add_seattle_data
    $ python manage.py add_fake_data
    ```

## Running the app

```
$ source env/bin/activate
$ python manage.py runserver
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
```

## Project Structure


```
├── Procfile
├── README.md
├── app
│   ├── __init__.py
│   ├── account
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── views.py
│   ├── admin
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── views.py
│   ├── assets
│   │   ├── scripts
│   │   │   ├── app.js
│   │   │   └── vendor
│   │   │       ├── jquery.min.js
│   │   │       ├── semantic.min.js
│   │   │       └── tablesort.min.js
│   │   └── styles
│   │       ├── app.scss
│   │       └── vendor
│   │           └── semantic.min.css
│   ├── assets.py
│   ├── decorators.py
│   ├── email.py
│   ├── main
│   │   ├── __init__.py
│   │   ├── errors.py
│   │   ├── forms.py
│   │   └── views.py
│   ├── models.py
│   ├── static
│   │   ├── fonts
│   │   │   └── vendor
│   │   ├── images
│   │   └── styles
│   │       └── app.css
│   ├── templates
│   │   ├── account
│   │   │   ├── email
│   │   │   ├── login.html
│   │   │   ├── manage.html
│   │   │   ├── register.html
│   │   │   ├── reset_password.html
│   │   │   └── unconfirmed.html
│   │   ├── admin
│   │   │   ├── index.html
│   │   │   ├── manage_user.html
│   │   │   ├── new_user.html
│   │   │   └── registered_users.html
│   │   ├── errors
│   │   ├── layouts
│   │   │   └── base.html
│   │   ├── macros
│   │   │   ├── form_macros.html
│   │   │   └── nav_macros.html
│   │   ├── main
│   │   │   └── index.html
│   │   └── partials
│   │       ├── _flashes.html
│   │       └── _head.html
│   └── utils.py
├── config.py
├── manage.py
├── requirements
│   ├── common.txt
│   └── dev.txt
└── tests
    ├── test_basics.py
    └── test_user_model.py
```

## License
[MIT License](LICENSE.md)
