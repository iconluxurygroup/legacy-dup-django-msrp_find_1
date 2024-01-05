from django.urls import path
from msrp_app import views

urlpatterns = [
    path('submit/', views.submit_task, name='submit_task'),
    path('update/', views.content, name='update'),
    path('download/<str:file_name>/', views.download, name='download')
]