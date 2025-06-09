from django.urls import path
from core import views

app_name = 'core'

urlpatterns = [
    # Configuration URLs
    path('configurations/', views.configuration_list, name='configuration_list'),
    path('configurations/create/', views.configuration_create, name='configuration_create'),
    path('configurations/<int:pk>/edit/', views.configuration_edit, name='configuration_edit'),
    path('configurations/<int:pk>/delete/', views.configuration_delete, name='configuration_delete'),

    # Check URLs
    path('checks/', views.check_list, name='check_list'),
    path('checks/<int:pk>/', views.check_detail, name='check_detail'),
    path('run-check/', views.run_check, name='run_check'),
]
