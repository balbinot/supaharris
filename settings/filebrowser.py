# http://django-filebrowser.readthedocs.io/en/latest/settings.html
# FILEBROWSER_DIRECTORY = "/media/uploads"
FILEBROWSER_DEFAULT_PERMISSIONS = 0o644
FILEBROWSER_EXTENSIONS = {
    'Image': ['.jpg','.jpeg','.gif','.png','.tif','.tiff'],
    'Document': [], # ['.pdf','.doc','.rtf','.txt','.xls','.csv'],
    'Video': [], # ['.mov','.wmv','.mpeg','.mpg','.avi','.rm'],
    'Audio': [], # ['.mp3','.mp4','.wav','.aiff','.midi','.m4p']
}
FILEBROWSER_ADMIN_VERSIONS = ['big']  # 'thumbnail', 'small', 'medium', 'large'
from django.core.files.storage import FileSystemStorage
from filebrowser.sites import site
site.storage = FileSystemStorage(location="static", base_url="/static/")
site.directory = "img/"
