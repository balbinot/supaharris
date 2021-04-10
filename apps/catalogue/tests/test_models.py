from catalogue.models import Reference
from django.conf import settings
from django.test import TestCase


class AutoRetrieveReferenceDetailsTestCase(TestCase):
    def setUp(self):
        super().setUp()

    def test_reference_save_method_retrieves_data_from_ads_url(self):
        if not settings.ADS_API_TOKEN:
            return
        # Tests utils.py --> scrape_reference_details_from_new_ads
        for ads_url in [
            # Old ADS --> rewritten to new-style
            "http://adsabs.harvard.edu/abs/1996AJ....112.1487H",  # deprecated from Oct 2019 onwards
            "http://adswww.harvard.edu/abs/1996AJ....112.1487H",  # deprecated from Oct 2019 onwards
            # New ADS
            "http://ui.adswww.harvard.edu/abs/1996AJ....112.1487H",  # https only, should be rewritten
            "https://ui.adswww.harvard.edu/abs/1996AJ....112.1487H",  # adsabs only, should be rewritten
            "https://ui.adsabs.harvard.edu/abs/1996AJ....112.1487H",  # totally valid
        ]:
            r = Reference.objects.create(ads_url=ads_url)
            self.assertEqual(r.bib_code, "1996AJ....112.1487H")
            self.assertEqual(
                r.ads_url, "https://ui.adsabs.harvard.edu/abs/1996AJ....112.1487H"
            )
            self.assertEqual(r.journal, "aj")
            self.assertEqual(r.first_author, "Harris")
            self.assertEqual(r.year, 1996)
            self.assertEqual(r.month, 10)
            self.assertEqual(r.volume, "112")
            self.assertEqual(r.pages, "1487")
            self.assertEqual(
                r.title,
                "A Catalog of Parameters for Globular Clusters in the Milky Way",
            )
            r.delete()

        # Has booktitle --> \baas instead of journal
        ads_url = "https://ui.adsabs.harvard.edu/abs/1973BAAS....5..326M"
        r = Reference.objects.create(ads_url=ads_url)
        self.assertEqual(r.bib_code, "1973BAAS....5..326M")
        self.assertEqual(r.ads_url, ads_url)
        self.assertEqual(r.journal, "baas")
        self.assertEqual(r.first_author, "Miller")
        self.assertEqual(r.year, 1973)
        self.assertEqual(r.month, 6)
        self.assertEqual(r.volume, "5")
        self.assertEqual(r.pages, "326")
        self.assertEqual(
            r.title,
            "Distant OB Clusters or Associations in the Vela and Carina Sections of the Milky Way.",
        )
        r.delete()

    def test_reference_save_method_retrieves_data_from_arxiv(self):
        # Tests utils.py --> scrape_reference_details_from_arxiv
        for ads_url in [
            "https://arxiv.org/abs/1308.2257",
        ]:
            r = Reference.objects.create(ads_url=ads_url)
            self.assertEqual(r.ads_url, ads_url)
            self.assertEqual(r.bib_code, "1308.2257")
            self.assertEqual(r.journal, "arxiv")
            self.assertEqual(r.first_author, "Don A. Vandenberg")
            self.assertEqual(r.year, "2013")
            self.assertEqual(r.month, 8)
            self.assertEqual(
                r.title,
                "The Ages of 55 Globular Clusters as Determined Using an Improved delta V_TO^HB Method Along with Color-Magnitude Diagram Constraints, and Their Implications for Broader Issues",
            )
            r.delete()
