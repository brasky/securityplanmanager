from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('implementations/<int:control_pk>/add/', 
         views.add_implementation, name='add_implementation'),
    path('implementations/<int:control_pk>/edit', views.edit_implementations, name='edit_implementation'),
    path('implementations/<int:control_pk>/', views.implementations, name='implementations'),
    path('certifications/', views.certifications, name='certifications'),
    path('certification-test/', views.certifications_test, name='certification-test'),
]
