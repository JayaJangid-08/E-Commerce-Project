from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('my-profile/', views.my_profile, name='my-profile'),
    path('register/', views.registration, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('switch-active-role/', views.switch_active_role, name='switch-active-role'),
    path('refresh/token/', TokenRefreshView.as_view(), name='refresh-token'),
    path('addresses/', views.address_list, name='address-list'),
    path('address/<int:address_id>/', views.address_detail, name='address-detail'),
    path('assign-role/', views.assign_role, name='assign-role'),
    path('remove-add-role/', views.remove_add_role, name='switch_role'),
]