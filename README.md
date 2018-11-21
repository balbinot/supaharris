## **Dependencies**
- Python 3.6.3
- Django 2.0.7
- See and intall `requirements.txt` for full dependencies

## **Installation for development**
- Create virtualenvironment: `virtualenv venv`
- Activate virtualenv: `source venv/bin/activate`

- Install required packages: `pip install -r requirements.txt`
- Setup local settings: `cp supaharris/local.example supaharris/local.py`
- Edit `supaharris/local.py` to tailor to your machine.

- `python manage.py check`
- `python manage.py migrate`
- `python manage.py createsuperuser`
- `python manage.py runserver` (and leave running)
