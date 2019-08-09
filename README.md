## **Dependencies**
- Python 3.7.4
- Django 2.2.4
- See and intall `requirements.txt` for full dependencies

## **Installation for development**
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
- TODO: `python manage.py loaddata fixtures/parameters.json` 
- `python manage.py add_parameters` 
- `python manage.py add_data_from_harris_1996ed2010` 

### How to add additional databases?
- Datbases can be parsed and inserted into the SupaHarris database by creating 
  a new management command in `apps/catalogue/management/commands`. 
  We provide boilerplate to get going.
- `cp apps/catalogue/management/commands/add_data_from_boilerplate.py 
   apps/catalogue/management/commands/add_data_from_author_year.py`
- Implement `apps/catalogue/management/commands/add_data_from_author_year.py`
- `python manage.py add_data_from_author_year`


### Run the development server at http://localhost:8000
- `python manage.py runserver` (and leave running)


## **Running with Docker**
- Make sure Docker Engine and docker-compose are installed (see Docker docs)

### **Running with Django's built-in development server w/ sqlite3 database**
- Build the image: `docker build -t supaharris .`
- Run the server: `docker run --rm -it -v "$(pwd)":/supaharris -p 1337:1337 
  --name runserver supaharris bash -c "python manage.py runserver 0.0.0.0:1337"` (and leave running)
  - Visit the website at http://localhost:1337
- In a new terminal, one can attach to the container in an interactive session:
  - `docker exec -it runserver bash`


### **Running the full stack: nginx + uwsgi w/ mariadb (mysql) database**
- `./utils/generate_sslcert.sh`
- `docker-compose up -d mariadb`
  - On first launch, the database and user will be created (you don't have to do anything)
- `docker-compose build django nginx`
- `docker-compose up --build`
- In a new terminal, one can attach to the container in an interactive session:
  - `docker exec -it supaharris-django bash`
- Now add the initial data (run this command in the container!)
  - `python manage.py add_parameters` 
  - `python manage.py add_data_from_harris_1996ed2010` 
- Create a superuser (run this command in the container)
  - `python manage.py createsuperuser`
- Visit the website at https://localhost (and accept the self-signed 
  certificate warning of the browser)
