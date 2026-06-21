from django.urls import path
from . import views


urlpatterns = [
    # Courier profile
    path('profile/create/', views.create_courier_profile, name='create-courier-profile'),
    path('profile/', views.courier_profile, name='courier-profile'),
    path('<int:courier_id>/verify/', views.verify_courier, name='verify-courier'),
    # Courier list/detail
    path('', views.courier_list, name='courier-list'),
    path('<int:courier_id>/', views.courier_detail, name='courier-detail'),
    # Assigned deliveries
    path('assign/delivery/', views.assign_delivery, name='assign-delivery'),
    path('assigned/deliveries/', views.assigned_deliveries, name='assigned-deliveries'),
    path('assignments/<int:assignment_id>/', views.assignment_detail, name='assignment-detail'),
    path('assignments/<int:assignment_id>/status/', views.update_delivery_status, name='update-delivery-status'),
]


