# Answer me
Real-time Q&A Application inspired by Kahoot. A discovery project into Python Flask websockets with SocketIO, and an exploration on using technology to host events for student clubs.

<img src="https://github.com/choyiny/answer-me/blob/master/answer/static/images/MC.png" width="300">

This application was used for this event: https://www.facebook.com/events/1127839204040865/

# Development setup

## Setup

Note: This project *requires* Python 3.6+, Docker and Docker Compose installed. For Mac users, ensure you are using the correct version of Python because the OS preinstalls Python 2.7 and default `pip` and `python` commands execute in v2.7 rather than v3.x.

If you don't have Python 3 installed on your Mac, you can install [Homebrew](https://brew.sh/) and run `brew install python3` on your terminal.

1. Create a virtual environment for the project and activate it. Run `pip3 install virtualenv` if virtualenv is not installed on Python3.6+
```
$ virtualenv answer-me-venv --python=/usr/local/bin/python3
$ source answer-me-venv/bin/activate
```

2. Clone the repository to your directory
```
(answer-me-venv) $ git clone git@github.com:choyiny/answer-me.git
(answer-me-venv) $ cd answer-me
```

3. Install the required dependencies
```
(answer-me-venv) $ pip install -r answer/requirements.txt
```

4. Spin up the Dockerized database in postgres.
```
(answer-me-venv) $ docker-compose up -d
```

5. If using PyCharm as the IDE, set the Project Interpreter as the Python from your venv
    - PyCharm -> Preferences -> Project -> Project Interpreter
    - Settings (gear icon) -> Add
    - Select "Existing Interpreter"
    - Look for Python3.x in `answer-me-venv/bin/python3.x`

## How to run locally
1. Make sure you are in your virtualenv that you setup
```
$ source answer-me-venv/bin/activate
```
2. Start server
```
(answer-me-venv) $ cd answer-me
(answer-me-venv) $ FLASK_APP=answer.app flask run
```
3. You should now able to access the website index.
```
http://localhost:5000
```

## Resetting databases
1. Remove database volumes attached to docker-compose
```
$ docker-compose down -v
```
2. Restart the database containers to get a fresh database
```
$ docker-compose up --build -d
```
