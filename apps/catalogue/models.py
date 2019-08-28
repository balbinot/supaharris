from __future__ import unicode_literals

from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.utils.text import slugify

from jsonfield import JSONField

from accounts.models import UserModel
from utils import (
    scrape_reference_details_from_old_ads,
    scrape_reference_details_from_new_ads,
    scrape_reference_details_from_arxiv,
)



VALIDATE = 1
ACCEPTED = 2
REJECTED = 3

STATUS_CHOICES = (
    (VALIDATE, "To be validated"),
    (ACCEPTED, "Accepted"),
    (REJECTED, "Rejected"),
)


class Parameter(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, unique=True, blank=True)
    description = models.TextField(max_length=256, null=True, blank=True)
    unit = models.CharField(max_length=64, null=False, blank=True,
        help_text="Must comply with astropy.unit")
    scale = models.FloatField(null=False, blank=False,
        help_text="Scale by which parameters must be multiplied by")

    # Time stamps, and logging of who changed user info
    last_updated_by = models.ForeignKey(UserModel,
        on_delete=models.SET_NULL, blank=True, null=True,
        related_name="has_changed_parameters"
    )
    date_created = models.DateTimeField("Date Created", auto_now_add=True)
    date_updated = models.DateTimeField("Date Last Changed", auto_now=True)

    class Meta:
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Parameter, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalogue:parameter_detail", args=[self.slug])

    @property
    def api_url(self):
        return reverse("parameter-detail", args=[self.slug])

    def __str__(self):
        if self.unit:
           return "{} [{}]".format(self.name, self.unit)
        else:
           return "{}".format(self.name)


class Reference(models.Model):
    """ References to the literature have one required model field: ads_url.
        All other entries will automatically be retrieved on-save! """

    # List from: http://adswww.harvard.edu/abs_doc/aas_macros.html
    JOURNALS = (
        ("aj",       "Astronomical Journal"),
        ("actaa",    "Acta Astronomica"),
        ("araa",     "Annual Review of Astron and Astrophys"),
        ("arxiv",    "arXiv e-prints"),
        ("apj",      "Astrophysical Journal"),
        ("apjl",     "Astrophysical Journal: Letters"),
        ("apjs",     "Astrophysical Journal: Supplement"),
        ("ao",       "Applied Optics"),
        ("apss",     "Astrophysics and Space Science"),
        ("aap",      "Astronomy and Astrophysics"),
        ("aapr",     "Astronomy and Astrophysics Reviews"),
        ("aaps",     "Astronomy and Astrophysics), Supplement"),
        ("azh",      "Astronomicheskii Zhurnal"),
        ("baas",     "Bulletin of the AAS"),
        ("caa",      "Chinese Astronomy and Astrophysics"),
        ("cjaa",     "Chinese Journal of Astronomy and Astrophysics"),
        ("icarus",   "Icarus"),
        ("jcap",     "Journal of Cosmology and Astroparticle Physics"),
        ("jrasc",    "Journal of the RAS of Canada"),
        ("memras",   "Memoirs of the RAS"),
        ("mnras",    "Monthly Notices of the RAS"),
        ("na",       "New Astronomy"),
        ("nar",      "New Astronomy Review"),
        ("pra",      "Physical Review A: General Physics"),
        ("prb",      "Physical Review B: Solid State"),
        ("prc",      "Physical Review C"),
        ("prd",      "Physical Review D"),
        ("pre",      "Physical Review E"),
        ("prl",      "Physical Review Letters"),
        ("pasa",     "Publications of the Astron. Soc. of Australia"),
        ("pasp",     "Publications of the ASP"),
        ("pasj",     "Publications of the ASJ"),
        ("rmxaa",    "Revista Mexicana de Astronomia y Astrofisica"),
        ("qjras",    "Quarterly Journal of the RAS"),
        ("skytel",   "Sky and Telescope"),
        ("solphys",  "Solar Physics"),
        ("sovast",   "Soviet Astronomy"),
        ("ssr",      "Space Science Reviews"),
        ("zap",      "Zeitschrift fuer Astrophysik"),
        ("nat",      "Nature"),
        ("iaucirc",  "IAU Cirulars"),
        ("aplett",   "Astrophysics Letters"),
        ("apspr",    "Astrophysics Space Physics Research"),
        ("bain",     "Bulletin Astronomical Institute of the Netherlands"),
        ("fcp",      "Fundamental Cosmic Physics"),
        ("gca",      "Geochimica Cosmochimica Acta"),
        ("grl",      "Geophysics Research Letters"),
        ("jcp",      "Journal of Chemical Physics"),
        ("jgr",      "Journal of Geophysics Research"),
        ("jqsrt",    "Journal of Quantitiative Spectroscopy and Radiative Transfer"),
        ("memsai",   "Mem. Societa Astronomica Italiana"),
        ("nphysa",   "Nuclear Physics A"),
        ("physrep",  "Physics Reports"),
        ("physscr",  "Physica Scripta"),
        ("planss",   "Planetary Space Science"),
        ("procspie", "Proceedings of the SPIE"),
    )

    MONTHS = (
        (1, "January"), (2, "February"), (3, "March"), (4, "April"),
        (5, "May"), (6, "June"), (7, "July"), (8, "August"),
        (9, "September"), (10, "October"), (11, "November"), (12, "December"),
    )

    help_text = "Please insert the ADS/arXiv url. All other paramters will "
    help_text += "automatically be retrieved on save!. For example: '{0}'".format(
        "http://adsabs.harvard.edu/abs/1996AJ....112.1487H")
    ads_url = models.URLField("ADS url", max_length=254, unique=True,
        help_text=help_text)
    bib_code = models.CharField("Bibliographic Code [ADS/arXiv]",
        max_length=24, null=True, blank=True)

    slug = models.SlugField(max_length=64, unique=True, blank=True)

    # Fields that are auto-retrieved
    first_author = models.CharField(max_length=128, null=True, blank=True)
    authors = models.TextField(max_length=1024, null=True, blank=True)
    title = models.TextField(max_length=256, null=True, blank=True)
    # Alternatively, one could make this a ForeignKey relation....
    journal = models.CharField(max_length=8, null=True, blank=True,
        choices=JOURNALS)
    doi = models.CharField("DOI", max_length=32, null=True, blank=True)
    year = models.PositiveSmallIntegerField("Year of publication",
        null=True, blank=True)
    month = models.PositiveSmallIntegerField("Month of publication",
        null=True, blank=True, choices=MONTHS)
    volume = models.CharField(max_length=8, null=True, blank=True)
    pages = models.CharField(max_length=16, null=True, blank=True)

    # Time stamps, and logging of who changed user info
    last_updated_by = models.ForeignKey(UserModel,
        on_delete=models.SET_NULL, blank=True, null=True,
        related_name="has_changed_references"
    )
    date_created = models.DateTimeField("Date Created", auto_now_add=True)
    date_updated = models.DateTimeField("Date Last Changed", auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __init__(self, *args, **kwargs):
        # We sneak in request parameter which allows us to pass the request
        # to the model instance when the model is saved via the admin interface
        self.request = None
        super(Reference, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        details = None
        self.ads_url = self.ads_url.replace("https", "http")  # no https on ads
        if "ui.adsabs" in self.ads_url:
            self.ads_url = self.ads_url.replace("ui.adsabs", "adswww").replace("#abs", "abs")
        if "/abs/" in self.ads_url:  # this is true for ADS and arXiv urls
            self.bib_code = self.ads_url.split("/abs/")[1]
            self.slug = slugify(self.bib_code.replace(".", "-"))

        if "ui.adswww" in self.ads_url or "ui.adsabs" in self.ads_url:
            details = scrape_reference_details_from_new_ads(self.ads_url, dict(self.JOURNALS))
        elif "adswww" in self.ads_url or "adsabs" in self.ads_url:
            # TODO: perhaps do this in a pre-save signal instead :)
            details = scrape_reference_details_from_old_ads(self.ads_url, dict(self.JOURNALS))

        if "arxiv" in self.ads_url:
            details = scrape_reference_details_from_arxiv(self.ads_url, dict(self.JOURNALS))

        if details:
            if "first_author" in details.keys():
                self.first_author = details["first_author"][0:128]
            if "authors" in details.keys():
                self.authors = details["authors"][0:1024]
            if "title" in details.keys():
                self.title = details["title"][0:256]
            if "journal" in details.keys():
                self.journal = details["journal"]
            if "doi" in details.keys():
                doi = details["doi"][0:32]
                if "doi.org" not in doi:
                    doi = "https://doi.org/" + doi
                self.doi = doi
            if "year" in details.keys():
                self.year = details["year"][0:4]
            if "month" in details.keys():
                self.month = details["month"]
            if "volume" in details.keys():
                self.volume = details["volume"][0:8]
            if "pages" in details.keys():
                self.pages = details["pages"][0:16]
        else:
            # So we could not retrieve the data from ADS, bummer. Now, if the model
            # save method was called from the admin we can inform the user that
            # auto-retrieving data from ADS failed, but for this we need to
            # pass a message to the request. So we sneak the request in via
            # the admin form.
            if self.request:
                msg = "Wopsiedaysie, we could not auto-retrieve the reference "
                msg += "data from the bibtex entry at ADS, or from the arXiv. "
                msg += "Please enter the relevant information manually."
                messages.error(self.request, msg)
        super(Reference, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalogue:reference_detail", args=[self.slug])

    @property
    def api_url(self):
        return reverse("reference-detail", args=[self.slug])

    def __str__(self):
        if self.first_author and self.year:
            return "{0} ({1})".format(self.first_author, self.year)
        else:
            return self.slug


class AstroObjectClassification(models.Model):
    name = models.CharField("Name", max_length=64, unique=True)
    abbreviation = models.CharField("Abbreviation", max_length=16, null=True, blank=True)
    slug = models.SlugField(max_length=64, unique=True, blank=True)

    # Time stamps, and logging of who changed user info
    last_updated_by = models.ForeignKey(UserModel,
        on_delete=models.SET_NULL, blank=True, null=True,
        related_name="has_changed_astro_object_classifications"
    )
    date_created = models.DateTimeField("Date Created", auto_now_add=True)
    date_updated = models.DateTimeField("Date Last Changed", auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class AstroObject(models.Model):
    name = models.CharField("Name", max_length=64, unique=True)
    slug = models.SlugField(max_length=64, unique=True, blank=True)
    altname = models.CharField("Alternative Name",
        max_length=64, null=True, blank=True)

    classifications = models.ManyToManyField(AstroObjectClassification,
        verbose_name="classification", related_name="astro_objects", blank=True
    )

    # Time stamps, and logging of who changed user info
    last_updated_by = models.ForeignKey(UserModel,
        on_delete=models.SET_NULL, blank=True, null=True,
        related_name="has_changed_astro_objects"
    )
    date_created = models.DateTimeField("Date Created", auto_now_add=True)
    date_updated = models.DateTimeField("Date Last Changed", auto_now=True)

    class Meta:
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(AstroObject, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalogue:astro_object_detail", args=[self.slug])

    @property
    def api_url(self):
        return reverse("astroobject-detail", args=[self.slug])

    def __str__(self):
        if self.altname:
           return "{} ({})".format(self.name, self.altname)
        else:
           return "{}".format(self.name)


class Profile(models.Model):
    reference = models.ForeignKey(
        Reference, related_name="profiles", on_delete=models.CASCADE
    )

    astro_object = models.ForeignKey(
        AstroObject, related_name="profiles", on_delete=models.CASCADE
    )

    # TODO: restrict options of profile_type?
    profile_type = models.CharField(max_length=256, null=True, blank=True)
    profile = JSONField()
    model_parameters = JSONField()
    model_flavour = models.CharField(max_length=256, null=True, blank=True)

    # Time stamps, and logging of who changed user info
    last_updated_by = models.ForeignKey(UserModel,
        on_delete=models.SET_NULL, blank=True, null=True,
        related_name="has_changed_profiles"
    )
    date_created = models.DateTimeField("Date Created", auto_now_add=True)
    date_updated = models.DateTimeField("Date Last Changed", auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return  "{} - Ref: {}".format(self.astro_object.name, self.astro_object.name)


class Auxiliary(models.Model):
    reference = models.ForeignKey(
        Reference, related_name="auxiliaries", on_delete=models.CASCADE
    )

    astro_object = models.ForeignKey(
        AstroObject, related_name="auxiliaries", on_delete=models.CASCADE
    )

    path = models.FilePathField(path="{0}".format(settings.STATIC_ROOT), blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    # Time stamps, and logging of who changed user info
    last_updated_by = models.ForeignKey(UserModel,
        on_delete=models.SET_NULL, blank=True, null=True,
        related_name="has_changed_auxiliaries"
    )
    date_created = models.DateTimeField("Date Created", auto_now_add=True)
    date_updated = models.DateTimeField("Date Last Changed", auto_now=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return "{} - Ref: {}".format(astro_object.name, str(reference))


class Observation(models.Model):
    reference = models.ForeignKey(
        Reference, related_name="observations", on_delete=models.CASCADE,
    )

    astro_object = models.ForeignKey(
        AstroObject, related_name="observations", on_delete=models.CASCADE,
    )

    parameter = models.ForeignKey(
        Parameter, related_name="observations", on_delete=models.CASCADE
    )

    value = models.CharField("Value", max_length=128, null=True, blank=True)
    sigma_up = models.CharField("Sigma up", max_length=128, null=True, blank=True)
    sigma_down = models.CharField("Sigma down", max_length=128, null=True, blank=True)

    # Time stamps, and logging of who changed user info
    last_updated_by = models.ForeignKey(UserModel,
        on_delete=models.SET_NULL, blank=True, null=True,
        related_name="has_changed_observations"
    )
    date_created = models.DateTimeField("Date Created", auto_now_add=True)
    date_updated = models.DateTimeField("Date Last Changed", auto_now=True)

    class Meta:
        ordering = ["-id"]

    def get_absolute_url(self):
        return reverse("catalogue:observation_detail", args=[self.slug])

    @property
    def api_url(self):
        return reverse("observation-detail", args=[self.slug])

    # This is how to print uncertainties in the columns of django-tables2
    @property
    def render_val(self):
        # TODO: take asymmetrical errors into account
        if self.sigma_up:
            return u"{:.3f} ± {:.3f}".format(self.value, self.sigma_up)
        elif self.value:
            return u"{:.3f}".format(self.value)
        else:
            return u"N/A"

    def __str__(self):
        # TODO: take asymmetrical errors into account
        if self.value and self.sigma_up and self.sigma_down:
            try:
                s = "{}: {} = {:.3f} + {:.3f} - {:.3f} ({})".format(
                    self.astro_object.name, self.parameter.name,
                    float(self.value), float(self.sigma_up), float(self.sigma_down),
                    str(self.reference))
            except ValueError as e:
                s = "{}: {} = {} + {} - {} ({})".format(
                    self.astro_object.name, self.parameter.name,
                    self.value, self.sigma_up, self.sigma_down,
                    str(self.reference))
        elif self.value:
            try:
                s = "{}: {} = {:.3f} ({})".format(
                    self.astro_object.name, self.parameter.name,
                    float(self.value), str(self.reference)
                )
            except ValueError as e:
                s = "{}: {} = {} ({})".format(
                    self.astro_object.name, self.parameter.name,
                    self.value, str(self.reference))
        else:
            s = "{}: {} = N/A ({})".format(
                self.astro_object.name, self.parameter.name,
                str(self.reference))
        return s


class Rank(models.Model):
    observation = models.ForeignKey(
        Observation, related_name="ranks", on_delete=models.CASCADE
    )

    rank = models.IntegerField()
    weight = models.IntegerField()
    compilation_name = models.CharField(
        max_length=64, null=True, blank=True)

    # Time stamps, and logging of who changed user info
    last_updated_by = models.ForeignKey(UserModel,
        on_delete=models.SET_NULL, blank=True, null=True,
        related_name="has_changed_ranks"
    )
    date_created = models.DateTimeField("Date Created", auto_now_add=True)
    date_updated = models.DateTimeField("Date Last Changed", auto_now=True)

    class Meta:
        ordering = ["-id"]
