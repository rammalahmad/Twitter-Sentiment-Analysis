- [Information](#information)
- [Online](#online)
  - [Deploy to Cloud Run](#deploy-to-cloud-run)
  - [Run locally](#run-locally)
  - [Run in shell](#run-in-shell)
  - [Changes to database structure](#changes-to-database-structure)
  - [Help](#help)
  - [Django Settings](#django-settings)
  - [Scripts](#scripts)
- [Offline](#offline)


--------
# Information


This file will serve as a full documentation on the two concieved models
of "Surf Mes Tweets", the twitter sentiment analysis tool of SurfMetrics\
\
Made by: Ahmad Rammal \
Original date: 31/08/2022 \
Last update: 31/08/2022

--------

# Model 1: The Datascientist Model

## Deploy to Cloud Run

To deploy the surfmetrics application to Cloud Run, go to the folder where all the files for the surfmetrics application are stored.
This folder should have the name 'surfmetrics', corresponding with the name of the github repository.

Go to the frontend directory:

```console
cd frontend/
```

Create a build of the application.

```console
npm run build
```

Go back to the main directory

```console
cd ../
```

```console
python manage.py collectstatic
```

Deploy the application to google cloud. Make sure the gli commands are installed (https://cloud.google.com/sdk/gcloud). This will take a few minutes.

```console
gcloud app deploy
```

## Run locally

To run the surfmetrics application locally, execute the following steps.

Go to the frontend directory:

```console
cd frontend/
```

Create a build of the application.

```console
npm run build
```

Go back to the main directory

```console
cd ../
```

```console
python manage.py runserver 8000
```

The application will run on your local server on port 8000, you can set the port to a different one if you like.


## Run in shell

To run some commands in the shell. You can do some quick queries on the database for example.

```console
cd frontend/
```

Create a build of the application.

```console
npm run build
```

Go back to the main directory

```console
cd ../
```

```console
python manage.py shell
```

Now, you can have a look at companies that are stored in the database for example.

```python
>>> from api.models.company import Company
>>> Company.objects.all()
```

With the use of filters, you can analyse the data.

## Changes to database structure

When you are making changes to the database structure, those changes need to be saved. Do this using the following commands in the main directory called surfmetrics.

```console
python manage.py makemigrations
```

This command will pack all your changes in different migration files. It is very similar to a git commit command.

```console
python manage.py migrate
```

This command will actually apply all the changes to the database.


## Help

By using the help function, you can see all possible commands that you can use. You can always have a look there if you need further information.

```console
python manage.py help
```

## Django Settings


import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "surfmetrics.settings")

import django
django.setup()


## Scripts

Dockerfile -> how to run with output
python manage.py shell < script.py
custom command for often recurring scripts: https://stackoverflow.com/a/16853755 
install django-extensions
add django extensions to settings installed apps


# Offline


postman request to mimick end of queue: 
PUT request ```http://127.0.0.1:8000/api/parse/20270/```
header: key: content-type value: application/json
body: {    
    "keywords": [
        "paris prosecutor says referred",
        "bafflement among veterans",
        "risk-control codes",
        "middle-office people",
        "largest futures exchange",
        "socgen frenetically unwound",
        "also included trades",
        "bank says",
        "futures markets",
        "contacted socgen"
    ],
    "score": 36.175000000000004,
    "subjectivity": 0.38548,
    "summary": "Eurex, Europe's largest futures exchange, contacted SocGen about oddities in trading patterns in late 2007, which the Paris prosecutor says referred to Mr Kerviel's positions. The sheer size of Mr Kerviel's exposure, the losses on which tripled as SocGen frenetically unwound its positions between January 21st and 23rd, has caused most bafflement among veterans of the futures markets. Embarrassingly, it also included trades with other parts of SocGen. Access to risk-control codes did not necessarily require the skills of a seasoned hacker; the bank says he may simply have offered to input details of trades on behalf of middle-office people when there was lots of activity on the trading floor.",
    "title": "No Défense | The Economist",
    "topics": "Sport, Politics, Energy",
    "url": "https://www.economist.com/finance-and-economics/2008/01/31/no-defense"
}
