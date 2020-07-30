# Auth/Validation and user permissions microservice

[![Build Status](https://travis-ci.com/D076/summer-practice-2020-SBT.svg?branch=nightlyVersion)](https://travis-ci.com/D076/summer-practice-2020-SBT)
[![codecov](https://codecov.io/gh/D076/summer-practice-2020-SBT/branch/nightlyVersion/graph/badge.svg)](https://codecov.io/gh/D076/summer-practice-2020-SBT)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/D076/summer-practice-2020-SBT/badges/quality-score.png?b=nightlyVersion)](https://scrutinizer-ci.com/g/D076/summer-practice-2020-SBT/?branch=nightlyVersion)
[![Requirements Status](https://requires.io/github/D076/summer-practice-2020-SBT/requirements.svg?branch=nightlyVersion)](https://requires.io/github/D076/summer-practice-2020-SBT/requirements/?branch=nightlyVersion)
![GitHub last commit (branch)](https://img.shields.io/github/last-commit/D076/summer-practice-2020-SBT/nightlyVersion)
![GitHub contributors](https://img.shields.io/github/contributors/d076/summer-practice-2020-SBT)
[![Discord](https://img.shields.io/discord/315390629997838349)](https://discord.gg/ks5pT6U)

## Installation

Use the paсkage manager [pip](https://pip.pypa.io/en/stable/) and [virtualenv](https://virtualenv.pypa.io/en/latest/) for building.

#### Windows
```bash
git clone https://github.com/D076/summer-practice-2020-SBT/
cd summer-practice-2020-SBT
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
set APP_SETTINGS=config.DevelopmentConfig
set DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost/DBNAME
python manage.py runserver
```

#### Linux and macOS
```bash
git clone https://github.com/D076/summer-practice-2020-SBT/
cd summer-practice-2020-SBT
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
export APP_SETTINGS=config.DevelopmentConfig
export DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost/DBNAME
python3 manage.py runserver
```