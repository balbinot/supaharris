from django.contrib.staticfiles.templatetags.staticfiles import static

from about.models import ContactInfo


class ContactInfoDefault(object):
    def __init__(self):
        """ Hardcoded in case there is no ContactInfo object """

        self.webmaster_email_address = "halbesma@mpa-garching.mpg.de"


def set_contactinfo(request):
    contactinfo = ContactInfo.objects.first()
    if not contactinfo:
        contactinfo = ContactInfoDefault()
    webmaster_email_address = contactinfo.webmaster_email_address

    return { "webmaster_email_address": webmaster_email_address }


def set_meta_tags(request):
    page_title = "SupaHarris Catalogue"
    page_image = static("img/social_share.png")
    page_description = "SupaHarris Catalogue of Globular Clusters in the Milky Way"
    page_keywords = "Globular Clusters, Star Clusters, Milky Way, Observations, Database, Harris"
    og_image = page_image
    og_title = page_title
    twitter_card = ""
    twitter_site = "@SupaHarris"  # Twitter Handle!
    twitter_title = page_title
    twitter_description = page_description
    twitter_image = page_image
