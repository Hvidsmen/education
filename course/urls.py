from django.urls import path

from . import views
from . import views_login

urlpatterns = [
    path("", views.index, name="index"),
    path('list_course/', views.list_course, name='list_course'),
    path('list_course/<int:course_id>', views.course, name='course'),
    path('course_test/<int:course_id>', views.course_test_from, name='course_test'),
    path('course_test/result_course', views.course_result_test, name='course_result_test'),
    path('subscribe', views.subscribe, name='subscribe'),
    path('list_course_view', views.list_course_view, name='list_course_view'),


    path('login/', views.login_view, name='login'),

]
