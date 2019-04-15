# https://www.tinymce.com/docs/demo/full-featured/
TINYMCE_DEFAULT_CONFIG = {
  'selector': 'textarea',
  'height': 500,
  'theme': 'modern',
  'plugins': [
    'advlist autolink lists link image charmap print preview hr anchor pagebreak',
    'searchreplace wordcount visualblocks visualchars code fullscreen',
    'insertdatetime media nonbreaking save table contextmenu directionality',
    'emoticons template paste textcolor colorpicker textpattern imagetools codesample toc'
  ],
  'toolbar1': 'undo redo | insert | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image',
  'toolbar2': 'print preview image | forecolor backcolor emoticons | codesample',
  'image_advtab': True,
  'templates': [
    { 'title': 'Test template 1', 'content': 'Test 1' },
    { 'title': 'Test template 2', 'content': 'Test 2' }
  ],
  'content_css': [
    '//fonts.googleapis.com/css?family=Lato:300,300i,400,400i',
    '//www.tinymce.com/css/codepen.min.css',
    '/static/css/main.css',
  ],
}
# TINYMCE_SPELLCHECKER = True
TINYMCE_COMPRESSOR = True
TINYMCE_FILEBROWSER = True
TINYMCE_MINIMAL_CONFIG = {
    'selector': 'textarea',
    'height': 80,
    'width': 500,
    'menubar': False,
    'statusbar': False,
    'elementpath': False,
    'plugins': [
        'link paste autolink code',
    ],
    'toolbar1': 'undo redo | bold italic | bullist numlist outdent indent | link code',
    'toolbar2': ''
}
