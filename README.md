supaharris
======

**supaharris.com globular and star cluster database**

.. image:: https://travis-ci.org/tlrh314/supaharris.svg?branch=master
   :target: http://travis-ci.org/tlrh314/supaharris

.. image:: https://img.shields.io/badge/license-AGPL3-brightgreen.svg
   :target: https://github.com/tlrh314/supaharris/blob/master/LICENSE


| Reference | Parser | Status | Management command | Status |
|-----------|--------|--------|--------------------|--------|
| [Harris 1996, 2010 ed.](https://ui.adsabs.harvard.edu/abs/1996AJ....112.1487H/abstract) | [`parse_harris_1996ed2010.py`](data/parse_harris_1996ed2010.py) | Done | [`add_harris_1996ed2010.py`](apps/catalogue/management/commands/add_harris_1996ed2010.py) | Done
| [VandenBerg+ 2013](https://ui.adsabs.harvard.edu/abs/2013ApJ...775..134V/abstract) | [`parse_vandenberg_2013.py`](data/parse_vandenberg_2013.py) | Done | [`add_vandenberg_2013.py`](apps/catalogue/management/commands/add_vandenberg_2013.py) | Done
| [Bica+ 2019](https://ui.adsabs.harvard.edu/abs/2019AJ....157...12B/abstract) | [`parse_bica_2019.py`](data/parse_bica_2019.py) | Started | [`add_bica_2019.py`](apps/catalogue/management/commands/add_bica_2019.py) | Boilerplate
| [Hilker+ 2019](https://ui.adsabs.harvard.edu/abs/2019MNRAS.482.5138B/abstract) | [`parse_hilker_2019.py`](data/parse_hilker_2019.py) | Started | [`add_hilker_2019.py`](apps/catalogue/management/commands/add_hilker_2019.py) | Boilerplate



## **Dependencies**
- Python 3.7.4
- Django 2.2.4
- See and install `requirements.txt` for full dependencies

## How to add additional databases?

### Add data and parser
- Add the data you want to add in a subfolder of `data`, e.g. `data/MW_GCS_Harris1996e2010`
- Add a parser in the `data` folder, e.g. `data/parse_harris_1996ed2010.py`
- You could stop here and add, commit and push the data + parsers, and we'll handle
  inserting it into the database.
  - If you do stop here, it would be very helpful if you could provide a mapping 
    (dictionary) that converts the name/identifier (e.g. NGC, Messier) in the dataset
    you want to add to the [name that we use in the SupaHarris database](https://www.supaharris.com/catalogue/astro_object/list/)
  - See above, but mapping the parameter names in your database to the 
  [parameters we use in the SupaHarris database](https://www.supaharris.com/catalogue/parameter/list/)

### Add Django script to insert the parsed data into the database
- For this step it would be useful to have the development server running locally.
  Below you'll find three options to achieve this (in order of complexity).
- Parsed data can be inserted into the SupaHarris database by creating 
  a new management command (= a new python file) in the folder 
  `apps/catalogue/management/commands`. We provide boilerplate to get going! :-)
- `cp apps/catalogue/management/commands/add_author_year.py 
   apps/catalogue/management/commands/add_changemeauthor_changemeyear.py`,
   e.g. naming the file `add_harris_1996ed2010.py`
- Implement `apps/catalogue/management/commands/add_changemeauthor_changemeyear.py`
- `python manage.py add_changemeauthor_changemeyear`


## **Installation for development (Option 1)**
- Create virtualenvironment: `virtualenv venv`
- Activate virtualenv: `source venv/bin/activate`

- Install required packages: `pip install -r requirements.txt`
  - If you experience difficulties installting mysqlclient, 
    remove it from requirements.txt (and run with an sqlite3 database)
- Setup local settings: `cp settings/.env.example settings/.env`
- Edit `settings/.env` to tailor to your machine.

- `python manage.py check`
- `python manage.py migrate`
- `python manage.py createsuperuser`
- When using `SITE_ID = 1` in the settings module one must make sure that the 
  Site with id=1 exists. So first we delete all existing sites, then create
  one for localhost.
- `python manage.py shell -c 'from django.contrib.sites.models import Site; 
   Site.objects.all().delete(); Site.objects.create(id=1, name="localhost:8000",
   domain="localhost:8000")'`

### Add the initial data to the database
- `python manage.py loaddata fixtures/catalogue_AstroObjectClassification.json` 
- `python manage.py loaddata fixtures/catalogue_Parameter.json` 
- `python manage.py add_harris_1996ed2010` 
- `python manage.py add_vandenberg_2013` 

### Run the development server at http://localhost:8000
- `python manage.py runserver` (and leave running)


## **Alternatively, run with Docker (Option 2)**
- Make sure Docker Engine and docker-compose are installed (see Docker docs)

### **Running with Django's built-in development server w/ sqlite3 database (Option 2a)**
- Build the image: `docker build -t supaharris .`
- Run the server: `docker run --rm -it -v "$(pwd)/settings/.env:/supaharris/settings/.env" -v "$(pwd)":/supaharris -p 1337:1337 
  --name runserver supaharris bash -c "python manage.py runserver 0.0.0.0:1337"` (and leave running)
  - Visit the website at http://localhost:1337
- In a new terminal, one can execute commands in the running container. Load the fixtures:
  - `docker exec runserver bash -c "python manage.py loaddata fixtures/catalogue_Parameter.json"`
- In a new terminal, one can attach to the container in an interactive session:
  - `docker exec -it runserver bash`

### **Running the full stack: nginx + uwsgi w/ mariadb (mysql) database (Option 2b)**
- `./utils/generate_sslcert.sh`
- `docker-compose up -d mariadb`
  - On first launch, the database and user will be created (you don't have to do anything)
- `docker-compose build django nginx`
- `docker-compose up --build`
- In a new terminal, one can attach to the container in an interactive session:
  - `docker exec -it supaharris_django_1 bash`
- Now add the initial data (run this command in the container!)
  - `python manage.py loaddata fixtures/catalogue_AstroObjectClassification.json` 
  - `python manage.py loaddata fixtures/catalogue_Parameter.json` 
  - `python manage.py add_harris_1996ed2010` 
- Create a superuser (run this command in the container)
  - `python manage.py createsuperuser`
- Visit the website at https://localhost (and accept the self-signed 
  certificate warning of the browser)


## Optional, if frontend changes are required
- Install [NodeJS](https://nodejs.org/en/download/) with npm
- `cd staticfiles`
- `npm install`
- New packages can now be added, e.g. `npm install bokehjs`

#### Gulp Tasks

- `gulp` the default task that builds everything
- `gulp dev` browserSync opens the project in your default browser and live reloads when changes are made
- `gulp css` compiles SCSS files into CSS and minifies the compiled CSS
- `gulp js` minifies the themes JS file
- `gulp vendor` copies dependencies from node_modules to the vendor directory
