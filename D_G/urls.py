"""
URL configuration for D_G project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from server import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'login', views.Login.as_view()),
    path(r'user', views.Register.as_view()),
    path(r'room', views.Room.as_view()),
    path(r'join', views.Join.as_view()),
    path(r'start', views.Start.as_view()),
    path(r'lexicon', views.Lexicon.as_view()),
    path(r'work', views.Work.as_view()),
    path(r'submit', views.Submit.as_view()),
    path(r'round', views.Round.as_view()),
    path(r'vote', views.Vote.as_view()),
    path(r'exit', views.Exit.as_view()),
    path(r'ready',views.Ready.as_view()),
]
