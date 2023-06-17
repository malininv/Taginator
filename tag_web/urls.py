from django.urls import path
from . import views

app_name = 'tag_web'

urlpatterns = [
    path('', views.index, name='index'),
    path('auth/', views.auth, name='auth'),
]