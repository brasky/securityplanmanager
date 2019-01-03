from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('search/', views.search, name='search'),
	path('implementations/add', views.add_implementation, name='add_implemenetation'),
	path('implementations/', views.implementations, name='implementations'),
]

