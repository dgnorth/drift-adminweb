[![Build Status](https://travis-ci.org/dgnorth/drift-adminweb.svg?branch=develop)](https://travis-ci.com/dgnorth/drift-adminweb)
[![codecov](https://codecov.io/gh/dgnorth/drift-adminweb/branch/develop/graph/badge.svg)](https://codecov.io/gh/dgnorth/drift-adminweb)

# drift-adminweb
Administration portal for drift-base


## Installation:

This project depends on **drift-base** so both projects need to be cloned from GitHub and a shared Drift Config DB is required as well.
  
First prepare your workstation using [these instructions](https://github.com/dgnorth/drift/blob/develop/README.md#prepare-your-workstation) if you have not already done so.

Run the following commands to install **drift-base** and **drift-adminweb** in developer mode:

```bash
# Clone and configure the drift-base projectgit clone https://github.com/dgnorth/drift-base.gitcd drift-basepipenv install --devpipenv run dconf developer --shared
cd ..

git clone https://github.com/dgnorth/drift-adminweb.gitcd drift-adminweb
pipenv install --devpipenv run dconf developer --shared
```

## Run development server

To run a server locally:

```bash
# In drift-adminweb directory:
pipenv run dconf developer --shared --run
```

Server is running at [http://localhost:5000/](http://localhost:5000/)

Username and password is **admin** and **test**.