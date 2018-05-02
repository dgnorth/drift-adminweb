[![Build Status](https://travis-ci.org/dgnorth/drift-adminweb.svg?branch=develop)](https://travis-ci.com/dgnorth/drift-adminweb)
[![codecov](https://codecov.io/gh/dgnorth/drift-adminweb/branch/develop/graph/badge.svg)](https://codecov.io/gh/dgnorth/drift-adminweb)

# drift-adminweb
Administration portal for drift-base


## Installation:
Run the following commands to install this project in developer mode:

```bash
pip install --user pipenv
pipenv install --dev
```

Run the following commands to enable drift and drift-config in developer mode for this project:

```bash
pipenv shell  # Make sure the virtualenv is active

pip install -e "../drift[aws,test]"
pip install -e "../drift-config[s3-backend,redis-backend]"
```

## Run localserver
This starts a server on port 5000:

```bash
pipenv shell  # Make sure the virtualenv is active

export FLASK_APP=drift.devserver:app && export FLASK_ENV=development
flask run
```

Try it out here: 
[http://localhost:5000/](http://localhost:5000/)


Fun fact: It's also possible to run a server using *uwsgi*:

```bash
pipenv shell --site-packages  # Make sure the virtualenv is active

export FLASK_APP=drift.devserver:app && export FLASK_ENV=development
uwsgi --module=drift.devserver:app --http=0.0.0.0:5000 --venv `pipenv --venv` --chdir ./adminweb
```