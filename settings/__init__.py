from settings.base import *


# NB, Load the filebrowser settings after base to ensure SECRET_KEY is set
from filebrowser.sites import site
from django.core.files.storage import FileSystemStorage
site.storage = FileSystemStorage(
    location=STATIC_ROOT,
    base_url=STATIC_URL
)
site.directory = "img/"
