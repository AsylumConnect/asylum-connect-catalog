# AsylumConnect [![Circle CI](https://circleci.com/gh/hack4impact/asylum-connect-catalog.svg?style=svg)](https://circleci.com/gh/hack4impact/asylum-connect-catalog) [![Stories in Ready](https://badge.waffle.io/hack4impact/asylum-connect-catalog.png?label=ready&title=Ready)](https://waffle.io/hack4impact/asylum-connect-catalog) [![Code Climate](https://codeclimate.com/github/hack4impact/asylum-connect-catalog/badges/gpa.svg)](https://codeclimate.com/github/hack4impact/asylum-connect-catalog) [![Test Coverage](https://codeclimate.com/github/hack4impact/asylum-connect-catalog/badges/coverage.svg)](https://codeclimate.com/github/hack4impact/asylum-connect-catalog/coverage) [![Issue Count](https://codeclimate.com/github/hack4impact/asylum-connect-catalog/badges/issue_count.svg)](https://codeclimate.com/github/hack4impact/asylum-connect-catalog)
<img src="readme_media/logo@2x.png" width="400"/>

## Team Members

- Hunter Lightman
- Yoni Nachmany
- Hana Pearlman
- Veronica Wharton

AsylumConnect’s current resource verification model is a bottleneck, as volunteers must search for and independently verify resources for each city that the organization expands into. In addition, volunteers are not (all) members of their target community, and therefore not the best-equipped to verify resource information. By allowing community members to tag, verify, endorse, and report resources, AsylumConnect will leverage its niche and highly marginalized community while also keeping members as safe as possible.

**Documentation available at [http://hack4impact.github.io/flask-base](http://hack4impact.github.io/flask-base).**

## What's included?

* Blueprints
* User and permissions management
* Flask-SQLAlchemy for databases
* Flask-WTF for forms
* Flask-Assets for asset management and SCSS compilation
* Flask-Mail for sending emails
* gzip compression
* Redis Queue for handling asynchronous tasks
* ZXCVBN password strength checker  
* CKEditor for editing pages

## Demos

Home Page:

![home](readme_media/home.gif "home") 

Registering User:

![registering](readme_media/register.gif "register")

Admin Homepage:

![admin](readme_media/admin.gif "admin")

Admin Editing Page:

![edit page](readme_media/editpage.gif "editpage") 

Admin Editing Users:

![edit user](readme_media/edituser.gif "edituser")

Admin Adding a User: 

![add user](readme_media/adduser.gif "add user")

## Setting up

##### Clone the repo

```
$ git clone https://github.com/hack4impact/asylum-connect-catalog.git
$ cd asylum-connect-catalog
```

##### Initialize a virtualenv

```
$ pip install virtualenv
$ virtualenv -p /path/to/python3.x/installation env
$ source env/bin/activate
```

For mac users it will most likely be
```
$ pip install virtualenv
$ virtualenv -p python3 env
$ source env/bin/activate
```

##### (If you're on a mac) Make sure xcode tools are installed

```
$ xcode-select --install
```

##### Add Environment Variables 

Create a file called `config.env` that contains environment variables in the following syntax: `ENVIRONMENT_VARIABLE=value`. For example,
the mailing environment variables can be set as the following. We recommend using Sendgrid for a mailing SMTP server. But anything else will work as well.
```
MAIL_USERNAME=SendgridUsername
MAIL_PASSWORD=SendgridPassword
SECRET_KEY=SuperRandomStringToBeUsedForEncryption
```
**Note: do not include the `.env` file in any commits. This should remain private.**

##### Install the dependencies

```
$ pip install -r requirements.txt
```

##### Other dependencies for running locally

You need to [Redis](http://redis.io/), and [Sass](http://sass-lang.com/). Chances are, these commands will work:


**Sass:**

```
$ gem install sass
```

**Redis:**

_Mac (using [homebrew](http://brew.sh/)):_

```
$ brew install redis
```

_Linux:_

```
$ sudo apt-get install redis-server
```

You will also need to install **PostgresQL**

_Mac (using homebrew):_

```
brew install postgresql
```

_Linux (based on this [issue](https://github.com/hack4impact/flask-base/issues/96)):_

```
sudo apt-get install libpq-dev
```


##### Create the database

```
$ python manage.py recreate_db
```

##### Other setup (e.g. creating roles in database)

```
$ python manage.py setup_dev
```

Note that this will create an admin user with email and password specified by the `ADMIN_EMAIL` and `ADMIN_PASSWORD` config variables. If not specified, they are both `flask-base-admin@example.com` and `password` respectively.


##### [Optional] Add Seattle data and fake data to the database

```
$ python manage.py add_seattle_data
```


##### [Optional] Add fake data to the database

```
$ python manage.py add_fake_data
```

## Running the app

```
$ source env/bin/activate
$ honcho start -f Local
```

## Formatting code

Before you submit changes to flask-base, you may want to auto format your code with `python manage.py format`.


## Contributing

Contributions are welcome! Check out our [Waffle board](https://waffle.io/hack4impact/flask-base) which automatically syncs with this project's GitHub issues. Please refer to our [Code of Conduct](./CONDUCT.md) for more information.

## Documentation Changes

To make changes to the documentation refer to the [Mkdocs documentation](http://www.mkdocs.org/#installation) for setup. 

To create a new documentation page, add a file to the `docs/` directory and edit `mkdocs.yml` to reference the file. 

When the new files are merged into `master` and pushed to github. Run `mkdocs gh-deploy` to update the online documentation.

## License
[MIT License](LICENSE.md)
