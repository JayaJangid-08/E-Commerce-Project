from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order-list'),
    path('place/', views.place_order, name='place-order'),
    path('<int:order_id>/', views.order_detail, name='order-detail'),
    path('<int:order_id>/cancel/',views.cancel_order, name='cancel-order'),
    path('<int:order_id>/status/',views.update_status, name='update-status'),
]