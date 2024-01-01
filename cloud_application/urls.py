# instances/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('generate_client_values/', generate_client_values, name='generate_client_values'),
    path('package_and_push_chart/<str:client_username>/', package_and_push_chart, name='package_and_push_chart'),
    path('', toindex, name='index'),
    path('ubuntu_instance', ubuntu_instance, name='ubuntu_instance'),

]
