from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.registration, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('refresh/token/', TokenRefreshView.as_view(), name='refresh-token'),
    path('addresses/', views.address_list, name='address-list'),
    path('address/<int:address_id>/', views.address_detail, name='address-detail'),
    path('assign-role/', views.assign_role, name='assign-role'),
    path('switch-role/', views.switch_role, name='switch_role'),
]