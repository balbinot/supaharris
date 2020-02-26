#!/bin/bash
set -e

echo -e "Deploying a fresh SupaHarris database instance, reading in all data"
docker exec -it supaharris_django_1 python manage.py check
echo

echo -e "1. Creating json dump of accounts data"
NOW=`date +%Y%m%d`
ACCOUNTS="accounts_${NOW}.json"
if [ -f "${ACCOUNTS}" ]; then
    rm "${ACCOUNTS}"
fi
docker exec supaharris_django_1 python manage.py \
    dumpdata accounts.UserModel > "${ACCOUNTS}"
echo -e "  json dump: $(ls ${ACCOUNTS})"

echo -e "\n2. Dropping database, and recreating it"
docker exec -it supaharris_mariadb_1 bash -c \
    'mysql -uroot -p$MYSQL_ROOT_PASSWORD -e "drop database supaharris;"'
docker exec -it supaharris_mariadb_1 bash -c \
    'mysql -uroot -p$MYSQL_ROOT_PASSWORD -e "create database supaharris;"'
docker exec -it supaharris_django_1 python manage.py migrate

echo -e "\n3. Loading fixtures"
echo -en "  AstroObjectClassification: "
docker exec supaharris_django_1 python manage.py \
    loaddata fixtures/catalogue_AstroObjectClassification.json
echo -en "  Parameter: "
docker exec supaharris_django_1 python manage.py \
    loaddata fixtures/catalogue_Parameter.json
echo -en "  Reference: "
docker exec supaharris_django_1 python manage.py \
    loaddata fixtures/references.json
echo -en "  Site: "
docker exec supaharris_django_1 python manage.py \
    loaddata fixtures/Site.json
echo -en "  UserModel: "
docker exec supaharris_django_1 python manage.py \
    loaddata "${ACCOUNTS}"

echo -e "\n4. Correcting Site instance [for localhost]"
docker exec supaharris_django_1 python manage.py shell -c '
from django.contrib.sites.models import Site; 
Site.objects.all().delete(); 
Site.objects.create(id=1, name="localhost:8000", domain="localhost:8000")
print("  {0}\n".format(Site.objects.all()))'

echo -e "5. Ingestion of databases"
docker exec supaharris_django_1 python manage.py add_harris_1996ed2010
docker exec supaharris_django_1 python manage.py add_vandenberg_2013
