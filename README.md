# Database Update Service: Active translators 

Schedule services:
- pull data from the database of sworn translators (authorised by the Romanian Ministry of Justice)
- correlate db with an internal list of contact details
- Gather translators by language and dump everything into a .docx file

![Python Version](https://img.shields.io/badge/python-3.12-blue)
![CI](https://github.com/mihai-mc/db-active-translators/actions/workflows/main.yaml/badge.svg)
![License](https://img.shields.io/github/license/mihai-mc/db-active-translators);

# Requirements

* Python 3.12
* pip3
* virtualenv

## Set up Virtual environment

``` python
    $ virtualenv --python=python3.12 env
    $ . env/bin/activate
```

## Install Dependencies

``` python
    $ pip install -r requirements.txt
```

## Convention

All scripts assume that they are being run from the root of the repo. Please adjust `PYTHONPATH` accordingly.
