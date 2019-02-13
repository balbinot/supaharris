## **Dependencies**
- Python 3.7.2
- Django 2.1.5
- See and intall `requirements.txt` for full dependencies

## **Installation for development**
- Create virtualenvironment: `virtualenv venv`
- Activate virtualenv: `source venv/bin/activate`

- Install required packages: `pip install -r requirements.txt`
- Setup local settings: `cp settings/local.example settings/local.py`
- Edit `settings/local.py` to tailor to your machine.

- `python manage.py check`
- `python manage.py migrate`
- `python manage.py createsuperuser`
- When using `SITE_ID = 1` in the settings module one must make sure that the 
  Site with id=1 exists. So first we delete all existing sites, then create
  one for localhost.
- `python manage.py shell -c 'from django.contrib.sites.models import Site; Site.objects.all().delete(); Site.objects.create(id=1, name="localhost:8000", domain="localhost:8000")'`

### Add the initial data to the database
- `python manage.py add_harris_data` 


### Run the development server at http://localhost:8000
- `python manage.py runserver` (and leave running)
