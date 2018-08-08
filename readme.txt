
pip install Django==1.6.10
pip install https://pypi.prezi.com/api/package/prezi_setuputils/prezi-setuputils-1.5.10.dev1.tar.gz
pip install https://pypi.prezi.com/api/package/prezi_swagger_django/prezi-swagger-django-0.0.273+gaf7c4f1.tar.gz

python manage.py runserver
# -> for some reason it does not find templates/swagger-keyword-extraction.yaml 
#    dir is supposed to be added in keyword_extraction/settings.py line 57
