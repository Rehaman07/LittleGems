from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('gallery/', views.gallery, name='gallery'),
    path('events/', views.events, name='events'),
    path('updates/', views.updates, name='updates'),
    path('admissions/', views.admissions, name='admissions'),
    path('contact/', views.contact, name='contact'),
    path('admin/' , views.admin, name='admin'),
    
    # Notice Board
    path('notices/', views.notice_list, name='notice_list'),
    
    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),

    # Authentication
    path('login/', views.login_user, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_user, name='logout'),

    # Homework
    path('homework/api/', views.homework_api, name='homework_api'),
]
