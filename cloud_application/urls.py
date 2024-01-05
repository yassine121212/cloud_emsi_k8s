# instances/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('generate_client_values/', generate_client_values, name='generate_client_values'),
    path('', toindex, name='index'),
    path('next_cloud_generate_service_client_values/', next_cloud_generate_service_client_values, name='next_cloud_generate_service_client_values'),
    path('next_cloud',next_cloud,name='next_cloud'),
    path('ubuntu_instance', ubuntu_instance, name='ubuntu_instance'),

]
