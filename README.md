# Auth/Validation and user permissions microservice

[![Build Status](https://travis-ci.com/D076/summer-practice-2020-SBT.svg?branch=master)](https://travis-ci.com/D076/summer-practice-2020-SBT)
[![codecov](https://codecov.io/gh/D076/summer-practice-2020-SBT/branch/master/graph/badge.svg)](https://codecov.io/gh/D076/summer-practice-2020-SBT)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/D076/summer-practice-2020-SBT/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/D076/summer-practice-2020-SBT/?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/caf52ef7185f43d48e1017f9a6686126)](https://www.codacy.com/manual/D076/summer-practice-2020-SBT?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=D076/summer-practice-2020-SBT&amp;utm_campaign=Badge_Grade)
[![Requirements Status](https://requires.io/github/D076/summer-practice-2020-SBT/requirements.svg?branch=master)](https://requires.io/github/D076/summer-practice-2020-SBT/requirements/?branch=master)
[![GitHub last commit (branch)](https://img.shields.io/github/last-commit/D076/summer-practice-2020-SBT/master)](https://github.com/D076/summer-practice-2020-SBT/commits/master)
[![GitHub contributors](https://img.shields.io/github/contributors/d076/summer-practice-2020-SBT)](https://github.com/D076/summer-practice-2020-SBT/graphs/contributors)
[![Discord](https://img.shields.io/discord/315390629997838349?color=Blue&label=Discord)](https://discord.gg/ks5pT6U)

## Installation

Use the paсkage manager [pip](https://pip.pypa.io/en/stable/) and [virtualenv](https://virtualenv.pypa.io/en/latest/) for building.

Edit **application.cfg**:
+  Step 1: Fills DATABASE_URL with your database login and password (postgresql://user:password@host/database)
+  Step 2 (Optionally): Fills gateway host and port

#### Windows
```bash
git clone https://github.com/D076/summer-practice-2020-SBT/
cd summer-practice-2020-SBT
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
python manage.py runserver [-h HOST] [-p PORT]
```

#### Linux and macOS
```bash
git clone https://github.com/D076/summer-practice-2020-SBT/
cd summer-practice-2020-SBT
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 manage.py db init
python3 manage.py db migrate
python3 manage.py db upgrade
python3 manage.py runserver [-h HOST] [-p PORT]
```

For generating roles and permissions run **roles_permissions.sql** script in your database.
