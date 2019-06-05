from django.urls import path

from . import views

app_name = 'simple_webpack'
urlpatterns = [
    path('', views.index, name='index'),
]
