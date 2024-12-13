from django.urls import path
from .views import robot_create_view, create_robot_web, robot_list_view

urlpatterns = [
    path('robots/', robot_create_view, name='robot-create'),
    path('robots/web/', create_robot_web, name='create_robot_web'),
    path('robots/list/', robot_list_view, name='robot-list'),
]
