from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings


urlpatterns = [
    path('home/', views.home, name="prt_home"),
    path('1D/', views.Onedimension, name="one_dimension"),
    path('2D/', views.Twodimension, name="two_dimension"),
    path('3D/', views.Threedimension, name="three_dimension"),
    path('view3D/', views.ViewThree, name="view_three"),
    path('2D/modeling', views.model, name="model"),
]
