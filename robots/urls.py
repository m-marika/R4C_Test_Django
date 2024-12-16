"""
URL configuration for robots.
"""
from django.urls import path
from .views import (
    robot_create_view,
    create_robot_web,
    robot_list_view,
    export_robots_summary,
)
urlpatterns = [
    path('robots/', robot_create_view, name='robot-create'),
    path('robots/web/', create_robot_web, name='create_robot_web'),
    path('robots/list/', robot_list_view, name='robot-list'),
    path('robots/export/', export_robots_summary, name='export-robots-summary'),
]
