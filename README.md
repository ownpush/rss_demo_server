<img src="https://ownpush.com/wp-content/uploads/2016/02/ownpush_128-logoSpelledout.png">

# Demo RSS Server #
## Overview ##
The purpose of this server is to showcase the type of developer server needed to interface with <a href="https://ownpush.com" target="_blank">OwnPush</a> as part of their application for secure, end-to-end encrypted push messaging without Google Services, and as such without a negative drain to the device's battery. The RSS Demo Server is part of the RSS Demo App, and can be setup via the following process:

## To start server

1. Create & Activate a virtualenv

2. Export the dev config 

```sh
$ export APP_SETTINGS="project.config.DevelopmentConfig"
```

3. Create DB

```sh
$ python manage.py create_db
$ python manage.py db init
```

4. Start the server

```sh
$ python manage.py runserver
```


## Key code files
As this demo server is based on a Flask Skeleton application only some of the files are worth noting


### ./project/rss/__init__.py
This file processes the RS feed and sends out push notifications where needed


### ./project/push/views.py
Defines the application register endpoint, this is used for the Android application to inform the server of what public push
ID to register and store in the DB


### ./project/push/tasks.py
This defines the finstions that generate the OwnPush style JWT tokens, encrypt the data using the APP private key and the INSTALL
public key and finaly sing the token