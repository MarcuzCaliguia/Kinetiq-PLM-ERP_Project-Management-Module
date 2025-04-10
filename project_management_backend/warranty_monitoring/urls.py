from django.urls import path
from . import views

urlpatterns = [
    path('', views.WarrantyListView.as_view(), name='warranty_list'),
    path('api/archive/', views.archive_warranties, name='archive_warranties'),
    path('api/restore/', views.restore_warranties, name='restore_warranties'),
]