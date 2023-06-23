from django.urls import path
from . import views

app_name = 'tag_web'

urlpatterns = [
    path('', views.index, name='index'),
    path('auth/', views.auth, name='auth'),
    path('login/', views.login_telegram, name='login'),
    path('update_content/', views.update_content, name='update_content'),
    path('update_session/', views.update_session, name='update_session'),
]